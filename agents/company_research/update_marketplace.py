#!/usr/bin/env python3
"""
Update Company Research Agent on the Agentify Marketplace
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

def update_agent(message: str):
    """Update an agent on the marketplace"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message
    }
    
    print(f"\n📤 Sending update request...")
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
    print("🔄 AGENTIFY MARKETPLACE - UPDATE COMPANY RESEARCH AGENT")
    print("=" * 80)
    
    print("\n📝 Updating Company Research Agent...")
    print("-" * 80)
    
    update_message = """Update the agent with ID agent.mossler.company_research with the following information:

Repository: https://github.com/JonasDEMA/agentify_os.git
Manifest URL: https://raw.githubusercontent.com/JonasDEMA/agentify_os/main/agents/company_research/manifest.json

The agent now includes:
- Live console logging in the web UI
- Real-time progress tracking
- Enhanced UI with 6 tabs: Upload, Analysis, Research, Results, Gap Analysis, Console
- Background task processing with async scraping
- LLM-powered data extraction using GPT-4o
- Configurable extraction fields
- Excel export functionality

Please update the repository URL and manifest URL for this agent."""

    result = update_agent(update_message)
    
    if result:
        print("\n\n" + "=" * 80)
        print("✅ UPDATE COMPLETE!")
        print("=" * 80)
        print("\n📋 Updated Information:")
        print("🔗 Agent ID: agent.mossler.company_research")
        print("🔗 Repository: https://github.com/JonasDEMA/agentify_os.git")
        print("🔗 Manifest: https://raw.githubusercontent.com/JonasDEMA/agentify_os/main/agents/company_research/manifest.json")
    else:
        print("\n\n" + "=" * 80)
        print("❌ UPDATE FAILED")
        print("=" * 80)
        print("\nPlease check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

