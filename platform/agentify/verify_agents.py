#!/usr/bin/env python3
"""
Verify Agentify Agents in the Marketplace
"""

import requests
import json

# Marketplace API Configuration (Note: endpoint URL is external service, 'orchestrator-agent' in URL is legacy naming)
MARKETPLACE_API = "https://uigsswdxmjqfccuxguxb.supabase.co/functions/v1/orchestrator-agent/chat"
API_KEY = "agfy_4c17ec3b634b11afd03e3ab003846729cc3837a56d1aafd57ae3647353239241"

def query_marketplace(message: str):
    """Query the marketplace"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message
    }
    
    print(f"\n📤 Query: {message}")
    
    try:
        response = requests.post(MARKETPLACE_API, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Response:")
        print(f"{result.get('response', 'No response message')}")
        
        if 'data' in result and result['data']:
            print(f"\n📊 Data:")
            print(json.dumps(result['data'], indent=2))
        
        if 'tools_used' in result:
            print(f"\n🔧 Tools used: {', '.join(result['tools_used'])}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def main():
    print("=" * 80)
    print("🔍 Agentify Agent Verification")
    print("=" * 80)
    
    # Search for calculation agents
    print("\n\n1️⃣  Searching for calculation agents...")
    print("-" * 80)
    query_marketplace("Find agents for calculation")
    
    # Get details for Calculation Agent
    print("\n\n2️⃣  Getting details for Calculation Agent...")
    print("-" * 80)
    query_marketplace("Give me details about agent.calculator.calculation")
    
    # Get details for Formatting Agent
    print("\n\n3️⃣  Getting details for Formatting Agent...")
    print("-" * 80)
    query_marketplace("Give me details about agent.calculator.formatting")
    
    # Get marketplace statistics
    print("\n\n4️⃣  Getting marketplace statistics...")
    print("-" * 80)
    query_marketplace("How many agents are in the marketplace?")
    
    print("\n\n" + "=" * 80)
    print("✅ Verification Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

