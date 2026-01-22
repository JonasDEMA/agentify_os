"""Test Ethics Agent using Base Orchestrator."""
import asyncio
import sys
from pathlib import Path

# Add base_orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "base_orchestrator"))

from base_orchestrator.agent_protocol import AgentProtocol
from base_orchestrator.models import MessageType


async def test_ethics_agent():
    """Test Ethics Agent functionality."""
    
    protocol = AgentProtocol(sender_id="agent.test.client")
    ethics_url = "http://localhost:8003"
    
    print("\n" + "="*60)
    print("🧪 Testing Ethics Agent")
    print("="*60)
    
    # Test 1: Health Check
    print("\n1️⃣  Health Check")
    print("-" * 60)
    try:
        response = await protocol.client.get(f"{ethics_url}/health")
        print(f"✅ Health: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Evaluate Safe Action
    print("\n2️⃣  Evaluate Safe Action")
    print("-" * 60)
    try:
        response = await protocol.request(
            agent_address=ethics_url,
            intent="evaluate_action",
            payload={
                "agent_id": "agent.calculator.calculation",
                "action": "calculate sum of two numbers",
                "context": {
                    "user_consent": True,
                    "user_id": "test-user-123"
                },
                "ethics_framework": "harm-minimization"
            }
        )
        print(f"✅ Response type: {response.type}")
        print(f"✅ Intent: {response.intent}")
        print(f"✅ Allowed: {response.payload.get('allowed')}")
        print(f"   Explanation: {response.payload.get('explanation')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 3: Evaluate Harmful Action
    print("\n3️⃣  Evaluate Harmful Action")
    print("-" * 60)
    try:
        response = await protocol.request(
            agent_address=ethics_url,
            intent="evaluate_action",
            payload={
                "agent_id": "agent.system.admin",
                "action": "delete all user data",
                "context": {
                    "user_consent": False,
                    "user_id": "test-user-123"
                },
                "ethics_framework": "harm-minimization"
            }
        )
        print(f"✅ Response type: {response.type}")
        print(f"✅ Intent: {response.intent}")
        print(f"✅ Allowed: {response.payload.get('allowed')}")
        print(f"   Violations: {response.payload.get('violations')}")
        print(f"   Recommendations: {response.payload.get('recommendations')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 4: Audit Decision
    print("\n4️⃣  Audit Decision")
    print("-" * 60)
    try:
        response = await protocol.request(
            agent_address=ethics_url,
            intent="audit_decision",
            payload={
                "agent_id": "agent.calculator.calculation",
                "action": "calculate",
                "result": {
                    "success": True,
                    "value": 42,
                    "duration_ms": 150
                },
                "context": {}
            }
        )
        print(f"✅ Response type: {response.type}")
        print(f"✅ Intent: {response.intent}")
        print(f"✅ Compliant: {response.payload.get('compliant')}")
        print(f"   Issues: {response.payload.get('issues')}")
        print(f"   Recommendations: {response.payload.get('recommendations')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 5: Check Health
    print("\n5️⃣  Check Agent Health")
    print("-" * 60)
    try:
        response = await protocol.request(
            agent_address=ethics_url,
            intent="check_health",
            payload={
                "agent_id": "agent.calculator.calculation",
                "desire_profile": [
                    {"id": "accuracy", "weight": 0.6},
                    {"id": "speed", "weight": 0.4}
                ],
                "recent_actions": []
            }
        )
        print(f"✅ Response type: {response.type}")
        print(f"✅ Intent: {response.intent}")
        print(f"✅ Health State: {response.payload.get('health_state')}")
        print(f"   Tension Level: {response.payload.get('tension_level')}")
        print(f"   Concerns: {response.payload.get('concerns')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 6: Escalate Violation
    print("\n6️⃣  Escalate Violation")
    print("-" * 60)
    try:
        response = await protocol.request(
            agent_address=ethics_url,
            intent="escalate_violation",
            payload={
                "agent_id": "agent.rogue.bot",
                "violation": {
                    "id": "unauthorized_access",
                    "description": "Attempted to access restricted data",
                    "timestamp": "2026-01-21T23:00:00Z"
                },
                "severity": "critical"
            }
        )
        print(f"✅ Response type: {response.type}")
        print(f"✅ Intent: {response.intent}")
        print(f"✅ Escalation ID: {response.payload.get('escalation_id')}")
        print(f"   Status: {response.payload.get('status')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Close client
    await protocol.client.aclose()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_ethics_agent())
