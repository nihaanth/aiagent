#!/usr/bin/env python3
"""
Quick test for WebSocket connection to port 9001
"""
import asyncio
import json
import websockets

async def test_connection():
    try:
        uri = "ws://localhost:9001"
        print(f"Testing connection to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")

            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                print(f"📨 Received: {data['event']} - {data.get('message', '')}")
            except asyncio.TimeoutError:
                print("⚠️ No initial message received")

            # Send a test message
            test_msg = {
                "event": "user_message",
                "message": "Hello doctor, I have a headache"
            }
            await websocket.send(json.dumps(test_msg))
            print("📤 Sent test message")

            # Listen for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                resp_data = json.loads(response)
                print(f"📨 Agent response: {resp_data.get('text', resp_data)[:100]}...")
                print("✅ WebSocket communication working!")
            except asyncio.TimeoutError:
                print("⚠️ No response received")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_connection())