#!/usr/bin/env python3
"""
Test the complete audio flow by simulating mobile app behavior
This will test if the backend can receive and process simulated audio
"""

import asyncio
import json
import base64
import websockets

async def test_audio_flow():
    try:
        print("🔗 Connecting to mobile bridge at ws://localhost:8080...")
        
        async with websockets.connect("ws://localhost:8080") as websocket:
            print("✅ Connected successfully!")
            
            # Simulate recording start
            print("📤 Sending recording start...")
            await websocket.send(json.dumps({
                "event": "recording_started",
                "timestamp": "2024-01-01T12:00:00Z"
            }))
            
            # Simulate audio chunks
            for i in range(3):
                print(f"📤 Sending audio chunk {i+1}/3...")
                
                # Create fake audio data (just some bytes)
                fake_audio = b"fake_audio_data_" + str(i).encode() * 100
                fake_audio_b64 = base64.b64encode(fake_audio).decode()
                
                await websocket.send(json.dumps({
                    "event": "audio_chunk",
                    "audio_data": fake_audio_b64,
                    "duration": (i + 1) * 1000,  # 1s, 2s, 3s
                    "timestamp": "2024-01-01T12:00:00Z"
                }))
                
                # Wait a bit between chunks
                await asyncio.sleep(1)
                
                # Listen for any responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    print(f"📥 Received response: {response}")
                except asyncio.TimeoutError:
                    pass
            
            # Simulate recording stop
            print("📤 Sending recording stop...")
            await websocket.send(json.dumps({
                "event": "recording_stopped",
                "timestamp": "2024-01-01T12:00:00Z"
            }))
            
            # Listen for final responses
            print("👂 Listening for final responses...")
            try:
                for _ in range(5):  # Try to get up to 5 messages
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    parsed = json.loads(response)
                    print(f"📥 Received: {parsed.get('event', 'unknown')} - {parsed.get('text', parsed.get('message', 'no text'))}")
            except asyncio.TimeoutError:
                print("⏰ No more responses")
                
            print("🏁 Audio flow test completed")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend running?")
        print("   Try: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Audio Flow Test")
    print("=" * 40)
    asyncio.run(test_audio_flow())