  #!/usr/bin/env python3
"""
Demo script to simulate a complete phone call conversation flow
This script demonstrates the conversation storage and retrieval functionality
"""
import asyncio
import json
import os
import secrets
import hashlib
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConversationDemo:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.sessions_collection = None

    async def setup_database(self):
        """Set up MongoDB connection"""
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "medical_agent")

        print(f"Connecting to MongoDB: {mongo_uri}")
        print(f"Database: {db_name}")

        try:
            self.mongo_client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
            await self.mongo_client.admin.command("ping")

            self.db = self.mongo_client[db_name]
            self.sessions_collection = self.db["call_sessions"]

            # Create indexes
            await self.sessions_collection.create_index("sessionId", unique=True)
            await self.sessions_collection.create_index([("phoneNumber", 1), ("updatedAt", -1)])

            print("✅ Database connection established")
            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def generate_passcode(self):
        """Generate a 6-digit passcode"""
        return "".join(secrets.choice("0123456789") for _ in range(6))

    def hash_passcode(self, passcode: str) -> str:
        """Hash a passcode for secure storage"""
        return hashlib.sha256(passcode.encode("utf-8")).hexdigest()

    async def simulate_phone_call(self):
        """Simulate a complete phone call conversation"""
        print("\n🎬 Starting phone call simulation...")

        # Generate session details
        session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        phone_number = "+15551234567"
        username = "John Doe"
        passcode = self.generate_passcode()
        passcode_hash = self.hash_passcode(passcode)
        call_sid = "demo_call_sid_123"

        print(f"📞 Simulating call from: {phone_number}")
        print(f"👤 Caller: {username}")
        print(f"🔐 Generated passcode: {passcode}")
        print(f"🆔 Session ID: {session_id}")

        # Create initial session document
        now = datetime.now(timezone.utc)
        session_doc = {
            "sessionId": session_id,
            "callSid": call_sid,
            "phoneNumber": phone_number,
            "username": username,
            "passcodeHash": passcode_hash,
            "status": "in_progress",
            "createdAt": now,
            "updatedAt": now,
            "messages": [],
            "functionCalls": [],
        }

        # Insert session
        await self.sessions_collection.insert_one(session_doc)
        print("✅ Session created in database")

        # Simulate conversation messages
        conversation_messages = [
            {
                "role": "user",
                "type": "transcription",
                "text": "Hello, I'm having a really bad headache and feel dizzy",
                "isFinal": True,
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "role": "assistant",
                "type": "agent_response",
                "text": "I understand you're experiencing head pain and dizziness. This could be caused by tension, dehydration, or stress. Can you tell me when this started and how severe it is on a scale of 1-10?",
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "role": "user",
                "type": "transcription",
                "text": "It started about 2 hours ago, and it's about a 7 out of 10. I also feel nauseous",
                "isFinal": True,
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "role": "assistant",
                "type": "agent_response",
                "text": "I'm going to assess your symptoms and recommend some next steps. The combination of headache, dizziness, and nausea could indicate several conditions.",
                "timestamp": datetime.now(timezone.utc)
            }
        ]

        # Add messages to database
        for message in conversation_messages:
            await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updatedAt": datetime.now(timezone.utc)}
                }
            )
            print(f"💬 Added message: {message['role']} - {message['text'][:50]}...")

        # Simulate function calls
        function_calls = [
            {
                "name": "assess_symptoms",
                "parameters": {
                    "symptoms": "headache, dizziness, nausea",
                    "severity": "7/10",
                    "duration": "2 hours"
                },
                "result": {
                    "patient_symptoms": "headache, dizziness, nausea",
                    "possible_conditions": [
                        {
                            "condition": "Tension headache with associated symptoms",
                            "recommendations": [
                                "rest in dark quiet room",
                                "hydration",
                                "over-the-counter pain relief",
                                "monitor symptoms",
                                "seek medical attention if symptoms worsen"
                            ]
                        },
                        {
                            "condition": "Possible migraine",
                            "recommendations": [
                                "rest",
                                "avoid triggers",
                                "consider migraine medication if available"
                            ]
                        }
                    ]
                },
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "name": "schedule_appointment",
                "parameters": {
                    "patient_name": username,
                    "reason": "headache, dizziness, and nausea assessment",
                    "urgency": "moderate"
                },
                "result": {
                    "appointment_id": 12345,
                    "message": "Appointment scheduled for tomorrow at 2:00 PM",
                    "date": "Tomorrow 2:00 PM",
                    "doctor": "Dr. Smith",
                    "location": "Main Clinic"
                },
                "timestamp": datetime.now(timezone.utc)
            }
        ]

        # Add function calls to database
        for func_call in function_calls:
            await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$push": {"functionCalls": func_call},
                    "$set": {"updatedAt": datetime.now(timezone.utc)}
                }
            )
            print(f"🔧 Added function call: {func_call['name']}")

        # End the call
        await self.sessions_collection.update_one(
            {"sessionId": session_id},
            {
                "$set": {
                    "status": "completed",
                    "endedAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )

        print("✅ Call simulation completed")
        print(f"📋 Session stored with ID: {session_id}")

        return {
            "session_id": session_id,
            "phone_number": phone_number,
            "passcode": passcode,
            "username": username
        }

    async def test_history_retrieval(self, phone_number, passcode):
        """Test retrieving conversation history"""
        print(f"\n🔍 Testing history retrieval...")
        print(f"📞 Phone: {phone_number}")
        print(f"🔐 Passcode: {passcode}")

        passcode_hash = self.hash_passcode(passcode)

        # Query for history
        query = {
            "phoneNumber": phone_number,
            "passcodeHash": passcode_hash
        }

        try:
            document = await self.sessions_collection.find_one(
                query,
                sort=[("updatedAt", -1)]
            )

            if document:
                print("✅ History retrieved successfully!")
                print(f"   - Session ID: {document['sessionId']}")
                print(f"   - Username: {document['username']}")
                print(f"   - Status: {document['status']}")
                print(f"   - Messages: {len(document['messages'])}")
                print(f"   - Function Calls: {len(document['functionCalls'])}")

                # Display conversation summary
                print("\n📝 Conversation Summary:")
                for i, msg in enumerate(document['messages'][:4], 1):
                    speaker = "👤 Patient" if msg['role'] == 'user' else "🤖 Dr. Claude"
                    print(f"   {i}. {speaker}: {msg['text'][:80]}...")

                print("\n🔧 Medical Functions Used:")
                for i, func in enumerate(document['functionCalls'], 1):
                    print(f"   {i}. {func['name']}")

                return document
            else:
                print("❌ No history found with provided credentials")
                return None

        except Exception as e:
            print(f"❌ Error retrieving history: {e}")
            return None

    async def test_wrong_credentials(self, phone_number):
        """Test with wrong credentials"""
        print(f"\n🚫 Testing with wrong credentials...")

        wrong_passcode = "999999"
        passcode_hash = self.hash_passcode(wrong_passcode)

        query = {
            "phoneNumber": phone_number,
            "passcodeHash": passcode_hash
        }

        document = await self.sessions_collection.find_one(query)

        if document:
            print("❌ Error: Wrong credentials should not return results!")
        else:
            print("✅ Security test passed: Wrong credentials rejected")

    async def cleanup_demo_data(self):
        """Clean up demo data"""
        print("\n🧹 Cleaning up demo data...")

        result = await self.sessions_collection.delete_many({
            "sessionId": {"$regex": "^demo_session_"}
        })

        print(f"✅ Cleaned up {result.deleted_count} demo records")

    async def run_demo(self):
        """Run the complete demo"""
        print("🎭 Medical Agent Conversation Demo")
        print("=" * 50)

        # Set up database
        if not await self.setup_database():
            return False

        try:
            # Simulate phone call
            session_info = await self.simulate_phone_call()

            # Test successful retrieval
            retrieved_history = await self.test_history_retrieval(
                session_info["phone_number"],
                session_info["passcode"]
            )

            # Test wrong credentials
            await self.test_wrong_credentials(session_info["phone_number"])

            # Show how to use in React app
            print("\n📱 To test in React app:")
            print(f"   1. Start the servers: python main.py")
            print(f"   2. Start the React app: cd pharmacy-app && npm start")
            print(f"   3. Click the history icon in the header")
            print(f"   4. Enter phone number: {session_info['phone_number']}")
            print(f"   5. Enter passcode: {session_info['passcode']}")

            print(f"\n🎉 Demo completed successfully!")

            # Ask if user wants to clean up
            cleanup = input("\n🧹 Clean up demo data? (y/n): ").lower().strip()
            if cleanup == 'y':
                await self.cleanup_demo_data()

            return True

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False

        finally:
            if self.mongo_client:
                self.mongo_client.close()

async def main():
    """Main function"""
    demo = ConversationDemo()
    success = await demo.run_demo()

    if success:
        print("\n✨ Demo completed successfully!")
        print("\nYour medical agent is ready with:")
        print("• 📞 Phone call conversation storage")
        print("• 🔐 Secure passcode authentication")
        print("• 📱 Mobile app history retrieval")
        print("• 🗄️ MongoDB persistence")
    else:
        print("\n⚠️ Demo encountered errors. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())