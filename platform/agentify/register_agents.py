#!/usr/bin/env python3
"""
Register Agentify Agents on the Marketplace
"""

import requests
import json

# Marketplace API Configuration (Note: endpoint URL is external service, 'orchestrator-agent' in URL is legacy naming)
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
    
    print(f"\n📤 Sending request...")
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
    print("🚀 Agentify Agent Registration")
    print("=" * 80)

    # Agent 1: Calculation Agent
    print("\n\n1️⃣  Registering Calculation Agent...")
    print("-" * 80)

    calc_message = """Register a new agent named 'Calculation Agent' with ID agent.calculator.calculation.

Description: Simple mathematical calculation agent for basic arithmetic operations
Capabilities: calculation (expert level) - Perform basic arithmetic operations
Version: 1.0.0
Status: active
Owner: Agentify (agents@meet-harmony.ai)
Tags: calculation, math, arithmetic
Pricing: 0.001 EUR per request
Repository: https://github.com/meet-harmony/calculation-agent
Build Type: docker
Host Requirements: 512 MB RAM, 0.5 CPU cores
Lifecycle Stage: production
SLA: 99.9%"""

    register_agent(calc_message)

    # Agent 2: Formatting Agent
    print("\n\n2️⃣  Registering Formatting Agent...")
    print("-" * 80)

    format_message = """Register a new agent named 'Formatting Agent' with ID agent.calculator.formatting.

Description: Number formatting agent with locale and decimal support
Capabilities: formatting (expert level), localization (high level)
Version: 1.0.0
Status: active
Owner: Agentify (agents@meet-harmony.ai)
Tags: formatting, localization, i18n
Pricing: 0.0005 EUR per request
Repository: https://github.com/meet-harmony/formatting-agent
Build Type: npm
Host Requirements: 256 MB RAM, 0.25 CPU cores
Lifecycle Stage: production
SLA: 99.9%"""

    register_agent(format_message)

    print("\n\n" + "=" * 80)
    print("✅ Registration Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

