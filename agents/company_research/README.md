# 🏢 Company Research Agent

**Agent ID:** `agent.mossler.company_research`  
**Version:** 1.0.0  
**Status:** ✅ Registered in Agentify Marketplace

---

## 📋 Overview

The Company Research Agent researches company information from websites and enriches Excel data. It extracts:

- **Managing Directors** (Geschäftsführer)
- **Company Size** (Revenue & Employees)
- **Company History** (if available)
- **Current News** (if available)

### Key Features

✅ **Excel Upload** - Upload Excel files with company data  
✅ **Gap Analysis** - Automatically identify missing information  
✅ **Configurable Extraction** - Choose which fields to extract  
✅ **Web Scraping** - Intelligent scraping with rate limiting  
✅ **Ethics-First** - Respects robots.txt and rate limits  

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd agents/company_research
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Locally

```bash
python main.py
```

The agent will start on `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get manifest
curl http://localhost:8000/agent/manifest

# Configure fields
curl -X POST http://localhost:8000/company/configure_fields \
  -H "Content-Type: application/json" \
  -d '{
    "managing_directors": true,
    "revenue": true,
    "employees": true,
    "history": false,
    "news": false
  }'
```

---

## 📖 API Endpoints

### Agent Standard Endpoints (Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/manifest` | GET | Get agent manifest |
| `/agent/reflect` | POST | Reflect on manifest |
| `/agent/governance` | GET | Get governance map |
| `/agent/collaborators` | GET | List collaborators |

### Company Research Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/company/upload_excel` | POST | Upload Excel file for gap analysis |
| `/company/configure_fields` | POST | Configure extraction fields |
| `/company/research` | POST | Research companies (TODO) |
| `/company/export` | POST | Export enriched data (TODO) |

---

## 🏗️ Project Structure

```
agents/company_research/
├── manifest.json          # Agent Standard v1 manifest
├── main.py               # FastAPI server & intents
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── register.py           # Marketplace registration script
├── .env.example          # Environment variables template
├── README.md             # This file
├── processors/           # Excel processing logic (TODO)
│   ├── __init__.py
│   ├── excel_reader.py
│   ├── excel_writer.py
│   └── gap_analyzer.py
└── scrapers/             # Web scraping logic (TODO)
    ├── __init__.py
    ├── company_scraper.py
    ├── data_extractor.py
    └── llm_extractor.py
```

---

## 🔧 Configuration

Edit `config.py` or set environment variables:

```python
# OpenAI
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1

# Web Scraping
RESPECT_ROBOTS_TXT=True
MIN_REQUEST_DELAY=1.0
RATE_LIMIT_REQUESTS=10

# Excel
MAX_FILE_SIZE_MB=50
SUPPORTED_FORMATS=["xlsx", "xls", "csv"]
```

---

## 📊 Usage Example

```python
import requests

# 1. Configure fields
response = requests.post(
    "http://localhost:8000/company/configure_fields",
    json={
        "managing_directors": True,
        "revenue": True,
        "employees": True,
        "history": False,
        "news": True
    }
)

# 2. Upload Excel file
with open("companies.xlsx", "rb") as f:
    response = requests.post(
        "http://localhost:8000/company/upload_excel",
        files={"file": f}
    )
    gap_analysis = response.json()["gap_analysis"]
    print(f"Missing data for {gap_analysis['incomplete_records']} companies")

# 3. Research companies (TODO)
# 4. Export enriched data (TODO)
```

---

## ✅ Next Steps (Implementation TODO)

- [ ] Implement Excel parsing (`processors/excel_reader.py`)
- [ ] Implement gap analysis (`processors/gap_analyzer.py`)
- [ ] Implement web scraping (`scrapers/company_scraper.py`)
- [ ] Implement LLM-based extraction (`scrapers/llm_extractor.py`)
- [ ] Implement research endpoint (`/company/research`)
- [ ] Implement export endpoint (`/company/export`)
- [ ] Add tests
- [ ] Deploy to Railway

---

## 🔗 Links

- **Marketplace:** https://marketplace.meet-harmony.ai
- **Repository:** https://github.com/JonasDEMA/agentify_os
- **Manifest:** [manifest.json](./manifest.json)
- **Agent Standard:** [docs/agent_standard/README.md](../../docs/agent_standard/README.md)

---

**Created:** 2026-01-27  
**Owner:** Mößler GmbH

