#!/usr/bin/env python3
"""
Test script for MongoDB connectivity and basic operations
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""

    # Get MongoDB URI from environment
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "medical_agent")

    print(f"Testing MongoDB connection to: {mongo_uri}")
    print(f"Database name: {db_name}")

    try:
        # Create client with timeout
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)

        # Test connection
        await client.admin.command("ping")
        print("✅ Successfully connected to MongoDB!")

        # Get database
        db = client[db_name]

        # Test collections
        call_sessions = db["call_sessions"]

        # Create a test session document
        test_session = {
            "sessionId": "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            "callSid": "test_call_123",
            "phoneNumber": "+1234567890",
            "username": "test_user",
            "passcodeHash": "test_hash_123",
            "status": "completed",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "messages": [
                {
                    "role": "user",
                    "type": "text_message",
                    "text": "Hello, I need help with my headache",
                    "timestamp": datetime.utcnow()
                },
                {
                    "role": "assistant",
                    "type": "agent_response",
                    "text": "I understand you're experiencing a headache. Can you tell me more about the symptoms?",
                    "timestamp": datetime.utcnow()
                }
            ],
            "functionCalls": [
                {
                    "name": "assess_symptoms",
                    "parameters": {"symptoms": "headache"},
                    "result": {"recommendation": "Rest and hydration"},
                    "timestamp": datetime.utcnow()
                }
            ]
        }

        # Insert test document
        result = await call_sessions.insert_one(test_session)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")

        # Query the document
        found_doc = await call_sessions.find_one({"sessionId": test_session["sessionId"]})
        if found_doc:
            print("✅ Successfully retrieved test document")
            print(f"   - Session ID: {found_doc['sessionId']}")
            print(f"   - Phone Number: {found_doc['phoneNumber']}")
            print(f"   - Messages: {len(found_doc['messages'])}")
            print(f"   - Function Calls: {len(found_doc['functionCalls'])}")

        # Create indexes for better performance
        await call_sessions.create_index("sessionId", unique=True)
        await call_sessions.create_index([("phoneNumber", 1), ("updatedAt", -1)])
        print("✅ Database indexes created")

        # Test authentication simulation (passcode verification)
        import hashlib
        test_passcode = "123456"
        passcode_hash = hashlib.sha256(test_passcode.encode("utf-8")).hexdigest()

        # Update the test document with the hashed passcode
        await call_sessions.update_one(
            {"sessionId": test_session["sessionId"]},
            {"$set": {"passcodeHash": passcode_hash}}
        )

        # Test authentication query
        auth_doc = await call_sessions.find_one({
            "phoneNumber": "+1234567890",
            "passcodeHash": passcode_hash
        })

        if auth_doc:
            print("✅ Passcode authentication test successful")
            print(f"   - Found session for phone +1234567890 with correct passcode")

        # Cleanup test document
        await call_sessions.delete_one({"sessionId": test_session["sessionId"]})
        print("✅ Test document cleaned up")

        # Close connection
        client.close()
        print("✅ MongoDB connection test completed successfully!")

        return True

    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MongoDB is installed and running locally")
        print("   - Install: brew install mongodb/brew/mongodb-community")
        print("   - Start: brew services start mongodb/brew/mongodb-community")
        print("2. Or update MONGODB_URI in .env to use MongoDB Atlas")
        print("3. Check firewall settings if using remote MongoDB")
        return False

async def main():
    """Main test function"""
    print("🧪 Starting MongoDB connectivity test...\n")

    success = await test_mongodb_connection()

    if success:
        print("\n🎉 All MongoDB tests passed! Your database is ready for conversation storage.")
    else:
        print("\n⚠️  MongoDB setup needed. Please follow the troubleshooting steps above.")

if __name__ == "__main__":
    asyncio.run(main())