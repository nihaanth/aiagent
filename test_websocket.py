#!/usr/bin/env python3
"""
Simple WebSocket test client to debug connectivity
Run this to test if the mobile bridge server is working
"""

import asyncio
import json
import websockets

async def test_websocket_connection():
    try:
        print("🔗 Connecting to mobile bridge at ws://localhost:8080...")
        
        async with websockets.connect("ws://localhost:8080") as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "event": "test",
                "message": "Hello from test client",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            print(f"📤 Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Send ping
            ping_message = {"command": "ping"}
            print(f"📤 Sending ping: {ping_message}")
            await websocket.send(json.dumps(ping_message))
            
            # Listen for responses
            print("👂 Listening for responses...")
            
            timeout_count = 0
            while timeout_count < 5:  # Listen for 5 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"📥 Received: {message}")
                    
                    # Parse and display nicely
                    try:
                        parsed = json.loads(message)
                        print(f"   Event: {parsed.get('event', 'unknown')}")
                        if 'message' in parsed:
                            print(f"   Message: {parsed['message']}")
                    except json.JSONDecodeError:
                        print("   (Could not parse as JSON)")
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏰ Timeout {timeout_count}/5")
                    
            print("🏁 Test completed")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend running?")
        print("   Try: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 WebSocket Connectivity Test")
    print("=" * 40)
    asyncio.run(test_websocket_connection())