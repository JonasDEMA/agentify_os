"""
Company Research Agent - Main Entry Point
"""

import json
import asyncio
import tempfile
import shutil
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import settings
from processors.excel_reader import ExcelReader
from processors.gap_analyzer import GapAnalyzer
from scrapers.company_scraper import CompanyScraper
from scrapers.llm_extractor import LLMExtractor
from job_state import JobStateManager

# Configure logging with daily rotation
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# File handler with daily rotation
file_handler = TimedRotatingFileHandler(
    filename=log_dir / "company_research.log",
    when="midnight",
    interval=1,
    backupCount=30,  # Keep 30 days of logs
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# Initialize FastAPI app
app = FastAPI(
    title=settings.agent_name,
    description="Research company information from websites and enrich Excel data",
    version=settings.agent_version
)

# Add CORS middleware
# Get CORS origins from environment variable or use defaults for local development
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize job state manager
job_state_manager = JobStateManager()


# Request/Response Models
class FieldConfig(BaseModel):
    """Configuration for fields to extract"""
    managing_directors: bool = True
    revenue: bool = True
    employees: bool = True
    history: bool = False
    news: bool = False
    custom_fields: list[str] = []


class CompanyData(BaseModel):
    """Company data structure"""
    name: str
    website: Optional[str] = None
    existing_data: Dict[str, Any] = {}


class ResearchRequest(BaseModel):
    """Research request"""
    companies: list[CompanyData]
    fields_to_extract: list[str]


class GapAnalysis(BaseModel):
    """Gap analysis result"""
    total_companies: int
    complete_records: int
    incomplete_records: int
    missing_fields: Dict[str, int]


# Load manifest
def load_manifest() -> Dict[str, Any]:
    """Load agent manifest"""
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Agent Standard Required Intents
@app.get("/agent/manifest")
async def get_manifest():
    """Get agent manifest (Required by Agent Standard)"""
    return load_manifest()


@app.post("/agent/reflect")
async def reflect_on_manifest(question: str):
    """Reflect on manifest (Required by Agent Standard)"""
    manifest = load_manifest()
    
    # Simple reflection logic
    if "capabilities" in question.lower():
        return {
            "answer": f"I have {len(manifest['capabilities'])} capabilities: " +
                     ", ".join([c['name'] for c in manifest['capabilities']])
        }
    elif "ethics" in question.lower():
        return {
            "answer": f"My ethics framework is {manifest['ethics']['framework']} with " +
                     f"{len(manifest['ethics']['hard_constraints'])} hard constraints"
        }
    else:
        return {"answer": "I am a company research agent that enriches Excel data with web-scraped information."}


@app.get("/agent/governance")
async def get_governance_map():
    """Get governance map (Required by Agent Standard)"""
    manifest = load_manifest()
    return {
        "instruction_authority": manifest["authority"]["instruction"],
        "oversight_authority": manifest["authority"]["oversight"],
        "escalation_channels": manifest["authority"]["escalation"]["channels"]
    }


@app.get("/agent/collaborators")
async def list_collaborators():
    """List collaborators (Required by Agent Standard)"""
    return {
        "collaborators": [],
        "message": "This agent currently works independently"
    }


# Global state (in production, use Redis or database)
uploaded_companies: List[Dict[str, Any]] = []
field_configuration: Dict[str, bool] = {
    "managing_directors": True,
    "revenue": True,
    "employees": True,
    "history": False,
    "news": False
}


# Company Research Intents
@app.post("/company/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload Excel file and perform gap analysis"""
    global uploaded_companies

    logger.info("=" * 80)
    logger.info("📤 UPLOAD REQUEST RECEIVED")
    logger.info(f"Filename: {file.filename}")
    logger.info(f"Content-Type: {file.content_type}")

    try:
        # Validate file type
        logger.info("🔍 Validating file type...")
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            logger.error(f"❌ Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported: .xlsx, .xls, .csv"
            )
        logger.info("✅ File type valid")

        # Save uploaded file to temp directory
        logger.info("💾 Saving file to temp directory...")
        temp_dir = Path(tempfile.gettempdir()) / "company_research"
        temp_dir.mkdir(exist_ok=True)
        logger.info(f"Temp directory: {temp_dir}")

        file_path = temp_dir / file.filename
        logger.info(f"File path: {file_path}")

        # Write file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size
        logger.info(f"✅ File saved successfully ({file_size} bytes)")

        # Read and parse Excel
        logger.info("📊 Reading Excel file...")
        reader = ExcelReader(file_path)
        df = reader.read()
        logger.info(f"✅ Excel read successfully")
        logger.info(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        logger.info(f"Column names: {list(df.columns)}")
        logger.info(f"Column mapping: {reader.column_mapping}")

        logger.info("🏢 Extracting companies...")
        companies = reader.extract_companies()
        logger.info(f"✅ Extracted {len(companies)} companies")

        if len(companies) > 0:
            logger.info(f"First company sample: {companies[0]}")

        # Store companies globally
        uploaded_companies = companies
        logger.info(f"✅ Stored {len(uploaded_companies)} companies globally")

        # Perform gap analysis
        logger.info("📈 Performing gap analysis...")
        required_fields = [
            field for field, enabled in field_configuration.items()
            if enabled
        ]
        logger.info(f"Required fields: {required_fields}")

        analyzer = GapAnalyzer(required_fields)
        gap_analysis = analyzer.analyze(companies)
        logger.info(f"✅ Gap analysis complete")
        logger.info(f"Gap analysis result: {gap_analysis}")

        response = {
            "success": True,
            "gap_analysis": gap_analysis,
            "companies": companies,
            "message": f"Successfully uploaded {len(companies)} companies"
        }

        logger.info("✅ UPLOAD SUCCESSFUL")
        logger.info("=" * 80)

        return response

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR DURING UPLOAD: {str(e)}")
        logger.exception(e)
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/company/configure_fields")
async def configure_fields(config: FieldConfig):
    """Configure which fields to extract"""
    global field_configuration

    logger.info("⚙️ CONFIGURE FIELDS REQUEST")
    logger.info(f"Config: {config}")

    field_configuration = {
        "managing_directors": config.managing_directors,
        "revenue": config.revenue,
        "employees": config.employees,
        "history": config.history,
        "news": config.news
    }

    configured = [field for field, enabled in field_configuration.items() if enabled]

    logger.info(f"✅ Configured fields: {configured}")

    return {
        "success": True,
        "configured_fields": configured,
        "message": f"Configured {len(configured)} fields for extraction"
    }


# Console logs storage (in production, use Redis or database)
console_logs: List[Dict[str, Any]] = []
MAX_CONSOLE_LOGS = 1000  # Keep last 1000 logs


class ConsoleLogHandler(logging.Handler):
    """Custom logging handler to capture logs for web console"""

    def emit(self, record):
        global console_logs

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": self.format(record)
        }

        console_logs.append(log_entry)

        # Keep only last MAX_CONSOLE_LOGS entries
        if len(console_logs) > MAX_CONSOLE_LOGS:
            console_logs = console_logs[-MAX_CONSOLE_LOGS:]


# Add console log handler to logger
console_handler = ConsoleLogHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)


async def research_background_task(job_id: str, companies: List[Dict[str, Any]], fields: List[str]):
    """Background task to perform research on companies with abort handling and rate limiting"""
    try:
        logger.info(f"🚀 Starting background research for job {job_id}")
        logger.info(f"📊 Total companies to process: {len(companies)}")
        logger.info(f"🔧 Fields to extract: {fields}")

        scraper = CompanyScraper()
        extractor = LLMExtractor()

        total = len(companies)
    except Exception as e:
        logger.error(f"❌ Fatal error initializing research task: {e}")
        logger.exception(e)
        try:
            job = job_state_manager.get_job(job_id)
            if job:
                job['status'] = 'failed'
                job['activity_log'].append({
                    'timestamp': datetime.now().isoformat(),
                    'message': f'❌ Fatal error: {str(e)}'
                })
                job_state_manager.save_job(job_id, job)
        except Exception as save_error:
            logger.error(f"❌ Failed to save error state: {save_error}")
        return

    for idx, company in enumerate(companies):
        try:
            # Check if abort was requested
            job = job_state_manager.get_job(job_id)
            if not job:
                logger.error(f"❌ Job {job_id} not found in database!")
                return

            if job.get('abort_requested'):
                logger.warning(f"🛑 Job {job_id} aborted by user at {idx}/{total}")
                job['status'] = 'aborted'
                job['activity_log'].append({
                    'timestamp': datetime.now().isoformat(),
                    'message': f'🛑 Research aborted by user at {idx}/{total}'
                })
                job_state_manager.save_job(job_id, job)
                return
            company_name = company.get('company_name', 'Unknown')
            website = company.get('website', '')

            logger.info(f"📊 Processing {idx + 1}/{total}: {company_name}")

            # Update current file and activity log
            job['current_file'] = company_name
            job["activity_log"].append({
                "timestamp": datetime.now().isoformat(),
                "message": f"Researching {company_name}..."
            })
            job_state_manager.save_job(job_id, job)

            if not website:
                logger.warning(f"⚠️  No website for {company_name}")
                job["activity_log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": f"⚠️  Skipped {company_name} - no website"
                })
                job["failed"] += 1
                job_state_manager.save_job(job_id, job)
                continue

            # Scrape website with timeout protection
            scrape_result = None
            try:
                scrape_result = await scraper.scrape_company(company_name, website, fields)
            except Exception as scrape_error:
                logger.error(f"❌ Scraping exception for {company_name}: {scrape_error}")
                scrape_result = {
                    "status": "failed",
                    "error": f"Scraping exception: {str(scrape_error)}"
                }

            if not scrape_result or scrape_result["status"] == "failed":
                logger.error(f"❌ Failed to scrape {company_name}")
                job["activity_log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": f"❌ Failed to scrape {company_name}"
                })
                job["failed"] += 1

                # Store failed result
                job["results"].append({
                    **company,
                    "research_status": "failed",
                    "error": scrape_result.get("error", "Unknown error") if scrape_result else "Scraping failed"
                })
                job_state_manager.save_job(job_id, job)
                continue

            # Extract data using LLM with error handling
            logger.info(f"🤖 Extracting data for {company_name} using LLM")
            collected_text = scrape_result.get("collected_text", "")

            if collected_text:
                try:
                    extraction_result = extractor.extract_company_info(collected_text, fields)
                    extracted_data = extraction_result.get("data", {})
                    confidence = extraction_result.get("confidence", {})
                except Exception as extract_error:
                    logger.error(f"❌ LLM extraction error for {company_name}: {extract_error}")
                    job["failed"] += 1
                    job["results"].append({
                        **company,
                        "research_status": "failed",
                        "error": f"LLM extraction failed: {str(extract_error)}"
                    })
                    job_state_manager.save_job(job_id, job)
                    continue

                logger.info(f"✅ Extracted data for {company_name}: {list(extracted_data.keys())}")

                # Merge with original company data
                enriched_company = {
                    **company,
                    **extracted_data,
                    "research_status": "success",
                    "sources": scrape_result.get("sources", []),
                    "confidence_scores": confidence
                }

                job["results"].append(enriched_company)
                job["completed"] += 1

                job["activity_log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": f"✅ Completed {company_name}"
                })
            else:
                logger.warning(f"⚠️  No text collected for {company_name}")
                job["failed"] += 1
                job["results"].append({
                    **company,
                    "research_status": "failed",
                    "error": "No text collected from website"
                })

            # Update progress and save state
            job["progress"] = int((idx + 1) / total * 100)
            job_state_manager.save_job(job_id, job)

        except Exception as e:
            logger.error(f"❌ Error processing {company.get('company_name', 'Unknown')}: {e}")
            logger.exception(e)

            try:
                job = job_state_manager.get_job(job_id)
                if job:
                    job["failed"] += 1
                    job["activity_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "message": f"❌ Error: {company.get('company_name', 'Unknown')} - {str(e)}"
                    })

                    job["results"].append({
                        **company,
                        "research_status": "error",
                        "error": str(e)
                    })
                    job_state_manager.save_job(job_id, job)
            except Exception as save_error:
                logger.error(f"❌ Failed to save error state: {save_error}")

        # Sleep to keep server responsive and avoid overwhelming APIs
        try:
            await asyncio.sleep(0.5)  # 500ms pause between companies
        except Exception as sleep_error:
            logger.error(f"❌ Sleep error: {sleep_error}")

    # Mark job as complete
    try:
        job = job_state_manager.get_job(job_id)
        if job:
            job["status"] = "completed"
            job["progress"] = 100
            job["current_file"] = None
            job["activity_log"].append({
                "timestamp": datetime.now().isoformat(),
                "message": f"🎉 Research completed! {job['completed']} successful, {job['failed']} failed"
            })
            job_state_manager.save_job(job_id, job)

        logger.info(f"✅ Background research completed for job {job_id}")
    except Exception as e:
        logger.error(f"❌ Error finalizing job {job_id}: {e}")
        logger.exception(e)


@app.post("/company/research")
async def start_research():
    """Start research process for uploaded companies"""
    global uploaded_companies, field_configuration

    logger.info("=" * 80)
    logger.info("🔍 RESEARCH REQUEST RECEIVED")
    logger.info(f"Companies to research: {len(uploaded_companies)}")
    logger.info(f"Field configuration: {field_configuration}")

    try:
        if not uploaded_companies:
            logger.error("❌ No companies uploaded")
            raise HTTPException(
                status_code=400,
                detail="No companies uploaded. Please upload an Excel file first."
            )

        # Generate job ID
        import uuid
        job_id = str(uuid.uuid4())
        logger.info(f"📋 Generated job ID: {job_id}")

        # Get enabled fields
        enabled_fields = [field for field, enabled in field_configuration.items() if enabled]
        logger.info(f"📋 Enabled fields: {enabled_fields}")

        # Initialize job in database
        job_data = {
            "status": "running",
            "progress": 0,
            "total": len(uploaded_companies),
            "completed": 0,
            "failed": 0,
            "current_file": None,
            "abort_requested": False,
            "results": [],
            "activity_log": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Started research for {len(uploaded_companies)} companies"
                }
            ],
            "created_at": datetime.now().isoformat()
        }
        job_state_manager.save_job(job_id, job_data)

        logger.info(f"✅ Job initialized in database: {job_id}")

        # Start background task
        asyncio.create_task(research_background_task(job_id, uploaded_companies.copy(), enabled_fields))

        logger.info(f"🚀 Background task started for job {job_id}")
        logger.info("=" * 80)

        return {
            "success": True,
            "job_id": job_id,
            "message": f"Research started for {len(uploaded_companies)} companies"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR STARTING RESEARCH: {str(e)}")
        logger.exception(e)
        logger.error("=" * 80)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to start research. Check logs for details."
            }
        )


@app.get("/company/research/{job_id}/progress")
async def get_research_progress(job_id: str):
    """Get research progress for a job"""
    logger.info(f"📊 Progress request for job: {job_id}")

    job = job_state_manager.get_job(job_id)
    if not job:
        logger.error(f"❌ Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "total": job["total"],
        "completed": job["completed"],
        "failed": job["failed"],
        "current_file": job.get("current_file"),
        "activity_log": job["activity_log"]
    }


@app.get("/company/research/{job_id}/results")
async def get_research_results(job_id: str):
    """Get research results for a job"""
    logger.info(f"📥 Results request for job: {job_id}")

    job = job_state_manager.get_job(job_id)
    if not job:
        logger.error(f"❌ Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "results": job["results"],
        "total": job["total"],
        "completed": job["completed"],
        "failed": job["failed"]
    }


@app.get("/company/export/{job_id}")
async def export_results(job_id: str):
    """Export research results to Excel"""
    import pandas as pd
    import tempfile
    from pathlib import Path

    logger.info(f"📤 Export request for job: {job_id}")

    job = job_state_manager.get_job(job_id)
    if not job:
        logger.error(f"❌ Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    results = job.get("results", [])

    if not results:
        logger.warning(f"⚠️  No results to export for job: {job_id}")
        raise HTTPException(status_code=400, detail="No results to export")

    try:
        # Convert results to DataFrame
        df = pd.DataFrame(results)

        # Create temp file
        temp_dir = Path(tempfile.gettempdir()) / "company_research"
        temp_dir.mkdir(exist_ok=True)

        export_file = temp_dir / f"research_results_{job_id[:8]}.xlsx"

        # Write to Excel
        df.to_excel(export_file, index=False, engine='openpyxl')

        logger.info(f"✅ Export file created: {export_file}")

        # Return file
        return FileResponse(
            path=export_file,
            filename=f"company_research_results.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/console/logs")
async def get_console_logs():
    """Get console logs for web display"""
    global console_logs

    return {
        "success": True,
        "logs": console_logs
    }


@app.post("/console/clear")
async def clear_console_logs():
    """Clear console logs"""
    global console_logs

    console_logs = []
    logger.info("🗑️  Console logs cleared")

    return {
        "success": True,
        "message": "Console logs cleared"
    }


@app.post("/company/research/{job_id}/abort")
async def abort_research(job_id: str):
    """Abort a running research job"""
    logger.info(f"🛑 Abort request for job: {job_id}")

    job = job_state_manager.get_job(job_id)
    if not job:
        logger.error(f"❌ Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "running":
        logger.warning(f"⚠️  Job {job_id} is not running (status: {job['status']})")
        return {
            "success": False,
            "message": f"Job is not running (status: {job['status']})"
        }

    # Request abort
    job_state_manager.request_abort(job_id)
    logger.info(f"🛑 Abort requested for job: {job_id}")

    return {
        "success": True,
        "message": "Abort requested. Job will stop after current company."
    }


@app.get("/company/active_jobs")
async def get_active_jobs():
    """Get all active research jobs"""
    logger.info("📋 Active jobs request")

    active_jobs = job_state_manager.get_active_jobs()

    return {
        "success": True,
        "jobs": active_jobs
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_id": settings.agent_id,
        "version": settings.agent_version
    }


if __name__ == "__main__":
    print(f"🚀 Starting {settings.agent_name} v{settings.agent_version}")
    print(f"📍 Agent ID: {settings.agent_id}")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )

