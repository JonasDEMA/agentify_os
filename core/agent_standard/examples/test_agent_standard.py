"""Test script for Agent Standard v1.

This script demonstrates:
1. Loading an agent manifest
2. Validating compliance
3. Creating an agent instance
4. Running the agent
5. Monitoring health and ethics
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.agent_standard import (
    Agent,
    AgentManifest,
    ManifestValidator,
    ComplianceChecker,
)


async def test_meeting_assistant():
    """Test the Meet Harmony meeting assistant agent."""
    print("\n" + "=" * 80)
    print("🤖 Agent Standard v1 - Test: Meet Harmony")
    print("=" * 80 + "\n")
    
    # 1. Load manifest
    print("📄 Loading manifest...")
    manifest_path = Path(__file__).parent / "meeting_assistant.json"
    manifest = AgentManifest.from_json_file(str(manifest_path))
    print(f"✅ Loaded: {manifest.name} v{manifest.version}")
    print(f"   Agent ID: {manifest.agent_id}")
    print(f"   Status: {manifest.status}")
    
    # 2. Validate manifest
    print("\n🔍 Validating manifest...")
    validator = ManifestValidator()
    result = validator.validate(manifest)
    
    if result.is_valid:
        print("✅ Manifest is valid!")
    else:
        print(f"❌ Manifest validation failed with {len(result.errors)} errors:")
        for error in result.errors:
            print(f"   - {error}")
        return
    
    if result.warnings:
        print(f"⚠️  {len(result.warnings)} warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # 3. Check compliance
    print("\n🔒 Checking Agent Standard v1 compliance...")
    checker = ComplianceChecker()
    compliance_result = checker.check_compliance(manifest)
    
    if compliance_result.is_valid:
        print("✅ Agent is COMPLIANT with Agent Standard v1!")
    else:
        print(f"❌ Compliance check failed:")
        for error in compliance_result.errors:
            print(f"   - {error}")
        return
    
    # 4. Display key information
    print("\n📊 Agent Configuration:")
    print(f"   Ethics Framework: {manifest.ethics.framework}")
    print(f"   Hard Constraints: {len(manifest.ethics.hard_constraints)}")
    print(f"   Ethical Principles: {len(manifest.ethics.principles)}")
    print(f"   Desires: {len(manifest.desires.profile)}")
    print(f"   Instruction Authority: {manifest.authority.instruction.id}")
    print(f"   Oversight Authority: {manifest.authority.oversight.id}")
    print(f"   Escalation Channels: {', '.join(manifest.authority.escalation.channels)}")
    
    # 5. Create agent instance
    print("\n🚀 Creating agent instance...")
    agent = Agent(manifest)
    print(f"✅ Agent created: {agent}")
    
    # 6. Start agent
    print("\n▶️  Starting agent...")
    await agent.start()
    print("✅ Agent started!")
    
    # 7. Check initial health
    print("\n💚 Checking agent health...")
    health = agent.get_health()
    print(f"   State: {health.state}")
    print(f"   Tension: {health.tension:.2f}")
    print(f"   Unsatisfied Desires: {len(health.unsatisfied_desires)}")
    
    # 8. Execute a test task
    print("\n⚡ Executing test task...")
    task = {
        "type": "summarize_meeting",
        "input": {
            "transcript": "Meeting about Q1 planning. Discussed budget and timeline.",
            "participants": ["Alice", "Bob", "Charlie"],
        },
    }
    
    result = await agent.execute(task)
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")
    
    # 9. Check health after execution
    print("\n💚 Checking health after execution...")
    health = agent.get_health()
    print(f"   State: {health.state}")
    print(f"   Tension: {health.tension:.2f}")
    
    # 10. Get agent status
    print("\n📈 Agent Status:")
    status = agent.get_status()
    print(f"   Executions: {status['execution_count']}")
    print(f"   Ethics Violations: {status['ethics_stats']['total_violations']}")
    print(f"   Ethics Warnings: {status['ethics_stats']['total_warnings']}")
    print(f"   Oversight Incidents: {status['oversight_stats']['total_incidents']}")
    
    # 11. Test incident reporting (non-punitive)
    print("\n📝 Testing non-punitive incident reporting...")
    incident = agent.report_incident(
        severity="warning",
        category="test_incident",
        message="This is a test incident - no consequences!",
        details={"test": True},
    )
    print(f"✅ Incident reported: {incident['category']}")
    
    # 12. Stop agent
    print("\n⏹️  Stopping agent...")
    await agent.stop()
    print("✅ Agent stopped!")
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80 + "\n")


async def main():
    """Main entry point."""
    try:
        await test_meeting_assistant()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

