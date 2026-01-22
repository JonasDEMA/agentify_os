"""Test Agent Communication with Agentify."""

import asyncio
import logging

from agents.desktop_rpa.agent_comm import AgentDiscovery, AgentRegistry
from agents.desktop_rpa.agent_comm.models import AgentRequest
from agents.desktop_rpa.config.agentify_config import agentify_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_discovery():
    """Test agent discovery."""
    print("\n" + "=" * 60)
    print("🧪 TEST 1: Agent Discovery")
    print("=" * 60)

    discovery = AgentDiscovery(
        api_token=agentify_config.api_token,
        gateway_url=agentify_config.gateway_url,
        sender_id=agentify_config.sender_id,
    )

    # Discover all agents
    print("\n1️⃣  Discovering all agents...")
    agents = await discovery.discover_agents()
    print(f"✅ Found {len(agents)} agents:")
    for agent in agents:
        print(f"   • {agent.name} (id={agent.id})")
        print(f"     Capabilities: {[cap.name for cap in agent.capabilities]}")
        print(f"     Status: {agent.status}")

    # Discover SMS agents
    print("\n2️⃣  Discovering SMS agents...")
    sms_agents = await discovery.discover_agents(capabilities_needed=["sms"])
    print(f"✅ Found {len(sms_agents)} SMS agents:")
    for agent in sms_agents:
        print(f"   • {agent.name} (id={agent.id})")

    print("\n" + "=" * 60)


async def test_find_agent():
    """Test finding agent by capability."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Find Agent by Capability")
    print("=" * 60)

    discovery = AgentDiscovery(
        api_token=agentify_config.api_token,
        gateway_url=agentify_config.gateway_url,
    )

    # Find SMS agent
    print("\n🔍 Finding SMS agent...")
    sms_agent = await discovery.find_agent_by_capability("sms")

    if sms_agent:
        print(f"✅ Found SMS agent: {sms_agent.name}")
        print(f"   ID: {sms_agent.id}")
        print(f"   Status: {sms_agent.status}")
        print(f"   Endpoint: {sms_agent.endpoint}")
    else:
        print("❌ No SMS agent found")

    # Find email agent
    print("\n🔍 Finding email agent...")
    email_agent = await discovery.find_agent_by_capability("email")

    if email_agent:
        print(f"✅ Found email agent: {email_agent.name}")
    else:
        print("❌ No email agent found")

    print("\n" + "=" * 60)


async def test_send_sms():
    """Test sending SMS."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Send SMS")
    print("=" * 60)

    discovery = AgentDiscovery(
        api_token=agentify_config.api_token,
        gateway_url=agentify_config.gateway_url,
    )

    # Find SMS agent
    print("\n🔍 Finding SMS agent...")
    sms_agent = await discovery.find_agent_by_capability("sms")

    if not sms_agent:
        print("❌ No SMS agent found, skipping test")
        return

    print(f"✅ Found SMS agent: {sms_agent.name}")

    # Send SMS
    print("\n📱 Sending test SMS...")
    request = AgentRequest(
        capability="sms",
        parameters={
            "recipient_number": "+49123456789",
            "message_text": "🤖 Test message from CPA Agent",
        },
        priority="normal",
    )

    response = await discovery.send_request(sms_agent, request)

    if response.success:
        print(f"✅ SMS sent successfully!")
        print(f"   Response: {response.data}")
    else:
        print(f"❌ Failed to send SMS: {response.error}")

    print("\n" + "=" * 60)


async def test_registry():
    """Test agent registry."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Agent Registry")
    print("=" * 60)

    registry = AgentRegistry()
    discovery = AgentDiscovery(
        api_token=agentify_config.api_token,
        gateway_url=agentify_config.gateway_url,
    )

    # Discover and register SMS agent
    print("\n1️⃣  Discovering SMS agent...")
    sms_agent = await discovery.find_agent_by_capability("sms")

    if sms_agent:
        print(f"✅ Found SMS agent: {sms_agent.name}")

        # Register
        print("\n2️⃣  Registering agent...")
        registry.register_agent(sms_agent)
        print(f"✅ Agent registered")

        # Get from registry
        print("\n3️⃣  Getting agent from registry...")
        cached_agent = registry.get_agent(sms_agent.id)
        if cached_agent:
            print(f"✅ Found in registry: {cached_agent.name}")
        else:
            print("❌ Not found in registry")

        # Get by capability
        print("\n4️⃣  Getting agents by capability...")
        sms_agents = registry.get_agents_by_capability("sms")
        print(f"✅ Found {len(sms_agents)} SMS agents in registry")

        # Get preferred agent
        print("\n5️⃣  Getting preferred agent...")
        preferred = registry.get_preferred_agent("sms")
        if preferred:
            print(f"✅ Preferred agent: {preferred.name}")
        else:
            print("❌ No preferred agent")

        # Registry summary
        print("\n6️⃣  Registry summary...")
        summary = registry.get_summary()
        print(f"   Total agents: {summary['total_agents']}")
        print(f"   Capabilities: {summary['capabilities']}")
        print(f"   Available agents: {summary['available_agents']}")

    else:
        print("❌ No SMS agent found, skipping registry test")

    print("\n" + "=" * 60)


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 AGENT COMMUNICATION TEST SUITE")
    print("=" * 60)
    print(f"\n📡 Gateway: {agentify_config.gateway_url}")
    print(f"🔑 Token: {agentify_config.api_token[:20]}...")
    print(f"👤 Sender: {agentify_config.sender_id}")
    print("\n" + "=" * 60)

    try:
        await test_discovery()
        await asyncio.sleep(1)

        await test_find_agent()
        await asyncio.sleep(1)

        await test_send_sms()
        await asyncio.sleep(1)

        await test_registry()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

