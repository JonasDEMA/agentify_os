"""Database seed script - Create admin token for Lovable UI."""
import asyncio
import secrets
from datetime import datetime

from sqlalchemy import select

from server.db.database import AsyncSessionLocal, engine
from server.db.models import Agent, Base


async def seed_database():
    """Seed database with admin token."""
    print("🌱 Seeding database...\n")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create admin agent for Lovable UI
    admin_token = "cpa_admin_lovable_ui_2025_secure_token_" + secrets.token_urlsafe(32)
    
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(Agent).where(Agent.id == "admin_lovable_ui")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("⚠️  Admin token already exists!")
            print(f"   Agent ID: {existing_admin.id}")
            print(f"   API Key: {existing_admin.api_key}")
            print("\n   To regenerate, delete the database and run seed again.")
            return
        
        # Create admin agent
        admin_agent = Agent(
            id="admin_lovable_ui",
            api_key=admin_token,
            os_name="Web",
            os_version="N/A",
            os_build="N/A",
            os_locale="en-US",
            hostname="lovable-ui",
            cpu_count=0,
            memory_total_gb=0.0,
            screen_resolution="N/A",
            dpi_scaling=1.0,
            ip_address="0.0.0.0",
            mac_address="00:00:00:00:00:00",
            python_version="N/A",
            agent_version="1.0.0",
            has_vision=False,
            has_ocr=False,
            has_ui_automation=False,
            phone_number=None,
            registered_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True,
            current_task="Lovable UI Admin Access",
        )
        
        session.add(admin_agent)
        await session.commit()
        
        print("✅ Admin token created successfully!\n")
        print("=" * 80)
        print("🔑 ADMIN TOKEN FOR LOVABLE UI")
        print("=" * 80)
        print(f"\nAgent ID: {admin_agent.id}")
        print(f"\nAPI Key:\n{admin_token}")
        print("\n" + "=" * 80)
        print("\n⚠️  WICHTIG: Speichere diesen Token sicher!")
        print("   - Verwende ihn in Lovable UI für API-Zugriff")
        print("   - Setze ihn als Environment Variable: VITE_CPA_API_KEY")
        print("   - Dieser Token wird nur einmal angezeigt!")
        print("\n" + "=" * 80)
        
        # Save to file for easy access
        with open(".admin_token.txt", "w") as f:
            f.write(f"Agent ID: {admin_agent.id}\n")
            f.write(f"API Key: {admin_token}\n")
            f.write(f"\nCreated: {datetime.utcnow().isoformat()}\n")
        
        print("\n💾 Token saved to: .admin_token.txt")
        print("   (Add this file to .gitignore!)\n")


if __name__ == "__main__":
    asyncio.run(seed_database())

