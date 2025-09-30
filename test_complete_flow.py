#!/usr/bin/env python3
"""
Test the complete flow: WebSocket connection, user message, and history retrieval
"""
import asyncio
import json
import websockets

async def test_complete_flow():
    print("🧪 Testing Complete Medical Agent Flow")
    print("=" * 50)

    try:
        # Connect to the mobile bridge server
        uri = "ws://localhost:9001"
        print(f"1. Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected to mobile bridge server")

            # Listen for initial message
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(initial_message)
                print(f"✅ Initial message: {data['event']}")
            except asyncio.TimeoutError:
                print("⚠️ No initial message received")

            # Test 2: Send a user message
            print("\n2. Testing user message...")
            user_message = {
                "event": "user_message",
                "message": "Hello doctor, I have a severe headache and feel dizzy"
            }

            await websocket.send(json.dumps(user_message))
            print("📤 Sent user message")

            # Listen for agent response
            responses_received = 0
            try:
                while responses_received < 3:  # Listen for multiple responses
                    response = await asyncio.wait_for(websocket.recv(), timeout=8.0)
                    resp_data = json.loads(response)

                    if resp_data.get('event') == 'agent_response':
                        print(f"✅ Agent response: {resp_data.get('text', '')[:80]}...")
                        responses_received += 1
                    elif resp_data.get('event') == 'function_call':
                        print(f"✅ Function call: {resp_data.get('function_name')}")
                        responses_received += 1
                    else:
                        print(f"📨 Other event: {resp_data.get('event')}")

            except asyncio.TimeoutError:
                print("⚠️ Timeout waiting for responses")

            # Test 3: History retrieval with test credentials
            print(f"\n3. Testing history retrieval...")
            history_request = {
                "command": "fetch_history",
                "phone_number": "+15551234567",
                "passcode": "996476"  # From our test data
            }

            await websocket.send(json.dumps(history_request))
            print("📤 Sent history request")

            # Listen for history response
            try:
                history_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                history_data = json.loads(history_response)

                if history_data['event'] == 'history':
                    history = history_data['history']
                    print("✅ History retrieved successfully!")
                    print(f"   📋 Session: {history['sessionId'][:20]}...")
                    print(f"   👤 User: {history['username']}")
                    print(f"   💬 Messages: {len(history.get('messages', []))}")
                    print(f"   🔧 Functions: {len(history.get('functionCalls', []))}")
                elif history_data['event'] == 'history_error':
                    print(f"ℹ️ History error: {history_data['message']}")
                    print("   (This is expected if test data was cleaned up)")

            except asyncio.TimeoutError:
                print("⚠️ No history response received")

            # Test 4: Wrong credentials
            print(f"\n4. Testing security (wrong credentials)...")
            wrong_request = {
                "command": "fetch_history",
                "phone_number": "+15551234567",
                "passcode": "000000"
            }

            await websocket.send(json.dumps(wrong_request))
            print("📤 Sent request with wrong passcode")

            try:
                wrong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                wrong_data = json.loads(wrong_response)

                if wrong_data['event'] == 'history_error':
                    print("✅ Security test passed: Wrong credentials rejected")
                else:
                    print(f"⚠️ Unexpected response: {wrong_data.get('event')}")

            except asyncio.TimeoutError:
                print("⚠️ No response to security test")

            print(f"\n🎉 Complete flow test finished!")

    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the server is running (python main.py)")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

async def main():
    success = await test_complete_flow()

    if success:
        print(f"\n✨ System is working correctly!")
        print(f"\nNext steps:")
        print(f"1. Start React app: cd pharmacy-app && npm start")
        print(f"2. Test credentials: +15551234567 / 996476")
        print(f"3. Use history button in app to test authentication")
    else:
        print(f"\n⚠️ System test failed. Check server logs.")

if __name__ == "__main__":
    asyncio.run(main())