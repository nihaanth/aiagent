#!/usr/bin/env python3
"""
Create test conversation data for demonstration
"""
import asyncio
from demo_conversation import ConversationDemo

async def create_test_data():
    demo = ConversationDemo()

    print("🎬 Creating test conversation data...")

    if await demo.setup_database():
        session_info = await demo.simulate_phone_call()

        print(f"\n✨ Test data created!")
        print(f"📱 To test in React app:")
        print(f"   Phone: {session_info['phone_number']}")
        print(f"   Passcode: {session_info['passcode']}")
        print(f"   Username: {session_info['username']}")

        return session_info

    return None

if __name__ == "__main__":
    asyncio.run(create_test_data())