#!/usr/bin/env python3
"""
Integration test for the medical agent WebSocket and database functionality
"""
import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_integration():
    """Test WebSocket connection and message handling"""
    print("🧪 Testing WebSocket integration...")

    try:
        # Connect to the mobile bridge server
        uri = "ws://localhost:8080"
        print(f"Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected to mobile bridge server")

            # Listen for initial connection message
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(initial_message)
                print(f"📨 Received: {data['event']}")

                if data['event'] == 'connection_established':
                    print("✅ Connection confirmed by server")

            except asyncio.TimeoutError:
                print("⚠️ No initial message received (timeout)")

            # Test sending a user message
            print("\n💬 Testing user message...")
            user_message = {
                "event": "user_message",
                "message": "Hello, I have a headache and feel dizzy",
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send(json.dumps(user_message))
            print("📤 Sent user message")

            # Listen for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                print(f"📨 Response: {response_data['event']}")

                if response_data['event'] == 'agent_response':
                    print(f"🤖 Agent said: {response_data['text'][:100]}...")
                    print("✅ Agent response received")

            except asyncio.TimeoutError:
                print("⚠️ No agent response received (timeout)")

            # Test history retrieval with demo data
            print("\n🔍 Testing history retrieval...")

            # Use the demo data from our previous test
            history_request = {
                "command": "fetch_history",
                "phone_number": "+15551234567",
                "passcode": "539919"  # This was from our demo
            }

            await websocket.send(json.dumps(history_request))
            print("📤 Sent history request")

            # Listen for history response
            try:
                history_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                history_data = json.loads(history_response)
                print(f"📨 History response: {history_data['event']}")

                if history_data['event'] == 'history':
                    history = history_data['history']
                    print(f"📋 Retrieved session: {history['sessionId']}")
                    print(f"👤 User: {history['username']}")
                    print(f"💬 Messages: {len(history.get('messages', []))}")
                    print(f"🔧 Functions: {len(history.get('functionCalls', []))}")
                    print("✅ History retrieval successful")
                elif history_data['event'] == 'history_error':
                    print(f"ℹ️ History error (expected if demo data was cleaned): {history_data['message']}")

            except asyncio.TimeoutError:
                print("⚠️ No history response received (timeout)")

            # Test wrong credentials
            print("\n🚫 Testing wrong credentials...")
            wrong_request = {
                "command": "fetch_history",
                "phone_number": "+15551234567",
                "passcode": "000000"  # Wrong passcode
            }

            await websocket.send(json.dumps(wrong_request))
            print("📤 Sent request with wrong passcode")

            try:
                wrong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                wrong_data = json.loads(wrong_response)

                if wrong_data['event'] == 'history_error':
                    print("✅ Security test passed: Wrong credentials rejected")
                else:
                    print(f"❌ Unexpected response: {wrong_data}")

            except asyncio.TimeoutError:
                print("⚠️ No response to wrong credentials")

            print("\n✨ WebSocket integration test completed!")

    except ConnectionRefusedError:
        print("❌ Connection refused. Is the server running? (python main.py)")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

async def main():
    """Main test function"""
    print("🧪 Medical Agent Integration Test")
    print("=" * 40)

    success = await test_websocket_integration()

    if success:
        print("\n🎉 Integration test completed!")
        print("\nNext steps:")
        print("1. Start React app: cd pharmacy-app && npm start")
        print("2. Test the mobile interface")
        print("3. Use history button to retrieve conversations")
    else:
        print("\n⚠️ Integration test failed. Check server status.")

if __name__ == "__main__":
    asyncio.run(main())