#!/usr/bin/env python3
"""
Register Company Research Agent on the Agentify Marketplace
"""

import requests
import json
import sys
import os

# Add parent directory to path to import from platform
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Marketplace API Configuration
MARKETPLACE_API = "https://uigsswdxmjqfccuxguxb.supabase.co/functions/v1/orchestrator-agent/chat"
API_KEY = "agfy_4c17ec3b634b11afd03e3ab003846729cc3837a56d1aafd57ae3647353239241"

def register_agent(message: str):
    """Register an agent on the marketplace"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message
    }
    
    print(f"\n📤 Sending registration request...")
    print(f"Message: {message[:100]}...")
    
    try:
        response = requests.post(MARKETPLACE_API, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Response: {result.get('response', 'No response message')}")
        
        if 'data' in result and result['data']:
            print(f"\nData: {json.dumps(result['data'], indent=2)}")
        
        if 'tools_used' in result:
            print(f"Tools used: {', '.join(result['tools_used'])}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def main():
    print("=" * 80)
    print("🏪 AGENTIFY MARKETPLACE - COMPANY RESEARCH AGENT REGISTRATION")
    print("=" * 80)
    
    print("\n📝 Registering Company Research Agent...")
    print("-" * 80)
    
    registration_message = """Register a new agent named 'Company Research Agent' with ID agent.mossler.company_research.

Description: Researches company information from websites and enriches Excel data. Extracts managing directors (Geschäftsführer), company size (revenue and employees), company history, and current news. Performs gap analysis to identify missing data and fills gaps through web scraping.

Capabilities:
- excel_processing (expert level) - Read and write Excel files, parse company data, perform gap analysis
- web_scraping (expert level) - Extract information from company websites using intelligent scraping
- data_extraction (expert level) - Extract structured data: managing directors, revenue, employees, history, news
- gap_analysis (expert level) - Compare existing data with user requirements and identify missing information
- configurable_extraction (high level) - User can configure which fields to extract from company websites

Version: 1.0.0
Status: active
Owner: Mößler GmbH (mossler@mossler.de)

Tags: company-research, web-scraping, excel-processing, data-enrichment, business-intelligence, b2b, lead-generation

Industries: finance, consulting, sales, marketing, business-intelligence

Use Cases: lead enrichment, company research, market analysis, sales intelligence, data enrichment

Pricing: 0.01 EUR per company researched

Repository: https://github.com/JonasDEMA/agentify_os
Manifest URL: https://raw.githubusercontent.com/JonasDEMA/agentify_os/main/agents/company_research/manifest.json

Build Type: python
Build Command: pip install -r requirements.txt
Start Command: python -m agents.company_research.main

Host Requirements: 1024 MB RAM, 1.0 CPU cores
Lifecycle Stage: development
SLA: best-effort

Tools Used: openpyxl, beautifulsoup4, scrapy, openai (GPT-4o)

Ethics Constraints:
- No unauthorized scraping
- Respect robots.txt
- Rate limiting required
- No data exfiltration

Visibility: public
Discoverable: true
Auto-register: true"""

    result = register_agent(registration_message)
    
    if result:
        print("\n\n" + "=" * 80)
        print("✅ REGISTRATION COMPLETE!")
        print("=" * 80)
        print("\n📋 Next Steps:")
        print("1. Verify registration at: https://marketplace.meet-harmony.ai")
        print("2. Implement agent logic in agents/company_research/main.py")
        print("3. Test locally: python -m agents.company_research.main")
        print("4. Deploy to Railway: railway up")
        print("\n🔗 Agent ID: agent.mossler.company_research")
        print("🔗 Manifest: agents/company_research/manifest.json")
    else:
        print("\n\n" + "=" * 80)
        print("❌ REGISTRATION FAILED")
        print("=" * 80)
        print("\nPlease check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

