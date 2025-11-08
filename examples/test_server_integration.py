"""Test server integration - Agent registration, logs, screenshots."""
import asyncio
from pathlib import Path

from agents.desktop_rpa.server_comm import AgentClient
from agents.desktop_rpa.vision.screenshot_manager import get_screenshot_manager


async def main():
    """Test server integration."""
    print("🚀 Testing CPA Server Integration\n")
    
    # 1. Create client
    print("1️⃣ Creating AgentClient...")
    client = AgentClient(server_url="http://localhost:8001")
    
    # 2. Register agent (if not already registered)
    if not client.is_registered:
        print("2️⃣ Registering agent...")
        response = await client.register(phone_number="+4915143233730")
        print(f"   ✅ Registered! Agent ID: {response.agent_id}")
        print(f"   🔑 API Key: {response.api_key[:20]}...")
    else:
        print(f"2️⃣ Already registered! Agent ID: {client.agent_id}")
    
    # 3. Send logs
    print("\n3️⃣ Sending logs...")
    await client.send_log("info", "Test started", task_goal="Test Server Integration")
    await client.send_log("thinking", "Analyzing task...", task_goal="Test Server Integration")
    await client.send_log("success", "Test completed successfully!", task_goal="Test Server Integration")
    print("   ✅ Logs sent!")
    
    # 4. Take screenshot and upload
    print("\n4️⃣ Taking screenshot...")
    screenshot_manager = get_screenshot_manager()
    
    # Take a simple screenshot
    screenshot_path = screenshot_manager.capture_screenshot_with_cursor(
        action_type="general",
        cursor_color="blue",
    )
    print(f"   📸 Screenshot saved: {screenshot_path}")
    
    # Upload screenshot
    print("   ⬆️ Uploading screenshot...")
    mouse_x, mouse_y = screenshot_manager.get_mouse_position()
    await client.upload_screenshot(
        screenshot_path=screenshot_path,
        action_type="general",
        mouse_x=mouse_x,
        mouse_y=mouse_y,
        task_goal="Test Server Integration",
    )
    print("   ✅ Screenshot uploaded!")
    
    # 5. Test before/after screenshot sequence
    print("\n5️⃣ Testing before/after screenshot sequence...")
    
    async def dummy_action():
        """Dummy action for testing."""
        await asyncio.sleep(0.5)
        print("   🎬 Action executed!")
    
    before, after = await screenshot_manager.capture_action_sequence(
        action_type="click",
        action_func=dummy_action,
        after_delay=2.0,  # 2 seconds instead of 3 for faster testing
    )
    
    print(f"   📸 Before: {before}")
    print(f"   📸 After: {after}")
    
    # Upload both
    print("   ⬆️ Uploading before/after screenshots...")
    
    mouse_x, mouse_y = screenshot_manager.get_mouse_position()
    
    await client.upload_screenshot(
        screenshot_path=before,
        action_type="before_click",
        mouse_x=mouse_x,
        mouse_y=mouse_y,
        task_goal="Test Server Integration",
    )
    
    await client.upload_screenshot(
        screenshot_path=after,
        action_type="after_click",
        mouse_x=mouse_x,
        mouse_y=mouse_y,
        task_goal="Test Server Integration",
    )
    
    print("   ✅ Before/After screenshots uploaded!")
    
    # 6. Final log
    await client.send_log("success", "All tests completed!", task_goal="Test Server Integration")
    
    # Close client
    await client.close()
    
    print("\n✅ All tests completed successfully!")
    print(f"\n📊 View results:")
    print(f"   - Server Docs: http://localhost:8001/docs")
    print(f"   - Agent Details: http://localhost:8001/api/v1/agents/{client.agent_id}")
    print(f"   - Logs: http://localhost:8001/api/v1/logs/?agent_id={client.agent_id}")
    print(f"   - Screenshots: http://localhost:8001/api/v1/screenshots/?agent_id={client.agent_id}")


if __name__ == "__main__":
    asyncio.run(main())

