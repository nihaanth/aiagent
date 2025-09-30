import asyncio
import json
import os
import secrets
import hashlib
import websockets
from typing import Optional, Tuple
from datetime import datetime, timezone

from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient

class MobileBridge:
    def __init__(self):
        self.mobile_clients = set()
        self.transcriptions = []
        self.agent_responses = []
        self.function_calls = []
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.sessions_collection = None
        self._db_initialized = False
        self.session_metadata = {}

    async def ensure_db(self):
        """Initialise MongoDB connection if configuration is present."""
        if self._db_initialized:
            return

        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            print("MONGODB_URI not set. Conversation persistence disabled.")
            self._db_initialized = True  # Avoid retrying every call
            return

        db_name = os.getenv("MONGODB_DB_NAME", "agent")

        try:
            client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Quick connectivity check
            await client.admin.command("ping")

            self.mongo_client = client
            self.db = client[db_name]
            self.sessions_collection = self.db["call_sessions"]

            # Helpful indexes for lookups
            await self.sessions_collection.create_index("sessionId", unique=True)
            await self.sessions_collection.create_index(
                [("phoneNumber", 1), ("updatedAt", -1)]
            )

            self._db_initialized = True
            print(f"MongoDB connected. Using database '{db_name}'.")
        except Exception as exc:
            print(f"Failed to initialise MongoDB: {exc}. Persistence disabled.")
            self._db_initialized = True
            self.mongo_client = None
            self.db = None
            self.sessions_collection = None

    def _serialise_for_client(self, data):
        if isinstance(data, datetime):
            return data.isoformat()
        if isinstance(data, ObjectId):
            return str(data)
        if isinstance(data, list):
            return [self._serialise_for_client(item) for item in data]
        if isinstance(data, dict):
            serialised = {}
            for key, value in data.items():
                if key == "passcodeHash":
                    continue
                serialised[key] = self._serialise_for_client(value)
            return serialised
        return data

    def _hash_passcode(self, passcode: str) -> str:
        return hashlib.sha256(passcode.encode("utf-8")).hexdigest()

    def _generate_passcode(self) -> str:
        return "".join(secrets.choice("0123456789") for _ in range(6))

    async def start_session(self, session_id: str, metadata: dict):
        """Register a new Twilio call session for persistence."""
        await self.ensure_db()

        phone_number = metadata.get("from", "unknown")
        call_sid = metadata.get("callSid")
        username = metadata.get("username") or metadata.get("caller") or phone_number
        passcode = self._generate_passcode()
        passcode_hash = self._hash_passcode(passcode)
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

        if self.sessions_collection is not None:
            try:
                await self.sessions_collection.update_one(
                    {"sessionId": session_id},
                    {
                        "$setOnInsert": session_doc,
                        "$set": {
                            "phoneNumber": phone_number,
                            "username": username,
                            "passcodeHash": passcode_hash,
                            "status": "in_progress",
                            "updatedAt": now,
                        },
                    },
                    upsert=True,
                )
            except Exception as exc:
                print(f"Failed to upsert session '{session_id}': {exc}")

        self.session_metadata[session_id] = {
            "phone_number": phone_number,
            "username": username,
            "passcode": passcode,
        }

        # Inform connected clients so they can surface credentials to staff
        await self.send_to_mobile(
            {
                "event": "session_started",
                "session_id": session_id,
                "phone_number": phone_number,
                "username": username,
                "passcode": passcode,
                "timestamp": now.isoformat(),
            }
        )

    async def end_session(self, session_id: str):
        """Mark a session as completed when a call ends."""
        await self.ensure_db()
        now = datetime.now(timezone.utc)

        if self.sessions_collection is not None:
            try:
                await self.sessions_collection.update_one(
                    {"sessionId": session_id},
                    {"$set": {"status": "completed", "endedAt": now, "updatedAt": now}},
                )
            except Exception as exc:
                print(f"Failed to mark session '{session_id}' complete: {exc}")

        if session_id in self.session_metadata:
            await self.send_to_mobile(
                {
                    "event": "session_completed",
                    "session_id": session_id,
                    "timestamp": now.isoformat(),
                }
            )
            self.session_metadata.pop(session_id, None)

    async def update_session_credentials(
        self,
        session_id: str,
        *,
        username: Optional[str] = None,
        passcode: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Allow mobile clients to set a custom username/passcode."""
        await self.ensure_db()

        if not session_id:
            return False, "session_id is required"

        if self.sessions_collection is None:
            return False, "Persistence not configured"

        update = {"updatedAt": datetime.now(timezone.utc)}
        if username:
            update["username"] = username
        if passcode:
            update["passcodeHash"] = self._hash_passcode(passcode)

        try:
            result = await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {"$set": update},
            )
        except Exception as exc:
            return False, f"Failed to update credentials: {exc}"

        if result.matched_count == 0:
            return False, "Session not found"

        local_meta = self.session_metadata.setdefault(session_id, {})
        if username:
            local_meta["username"] = username
        if passcode:
            local_meta["passcode"] = passcode

        return True, "Credentials updated"

    async def fetch_history(
        self,
        *,
        phone_number: str,
        passcode: str,
        session_id: Optional[str] = None,
    ):
        """Retrieve stored conversation history after verifying passcode."""
        await self.ensure_db()

        if self.sessions_collection is None:
            return None

        query = {"phoneNumber": phone_number, "passcodeHash": self._hash_passcode(passcode)}
        if session_id:
            query["sessionId"] = session_id

        try:
            document = await self.sessions_collection.find_one(
                query,
                sort=[("updatedAt", -1)],
            )
            return document
        except Exception as exc:
            print(f"Failed to fetch history: {exc}")
            return None

    async def _append_message(self, session_id: Optional[str], message: dict):
        await self.ensure_db()
        if not session_id or self.sessions_collection is None:
            return

        payload = {**message, "timestamp": datetime.now(timezone.utc)}

        try:
            await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {"$push": {"messages": payload}, "$set": {"updatedAt": datetime.now(timezone.utc)}},
                upsert=True,
            )
        except Exception as exc:
            print(f"Failed to append message for session '{session_id}': {exc}")

    async def _append_function_call(self, session_id: Optional[str], entry: dict):
        await self.ensure_db()
        if not session_id or self.sessions_collection is None:
            return

        payload = {**entry, "timestamp": datetime.now(timezone.utc)}

        try:
            await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$push": {"functionCalls": payload},
                    "$set": {"updatedAt": datetime.now(timezone.utc)},
                },
                upsert=True,
            )
        except Exception as exc:
            print(f"Failed to append function call for session '{session_id}': {exc}")

    async def store_conversation_buffer(self, session_id: str, conversation_buffer: list):
        """Store buffered conversation messages to MongoDB"""
        await self.ensure_db()
        if not session_id or self.sessions_collection is None:
            print(f"⚠️ Cannot store conversation: session_id={session_id}, collection={self.sessions_collection}")
            return

        if not conversation_buffer:
            return

        try:
            # Convert buffer messages to proper format for MongoDB
            formatted_messages = []
            for msg in conversation_buffer:
                # Prefer the original timestamp from the buffer when available
                timestamp_value = msg.get("timestamp")
                if isinstance(timestamp_value, datetime):
                    timestamp_dt = timestamp_value
                elif isinstance(timestamp_value, str):
                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp_value)
                        if timestamp_dt.tzinfo is None:
                            timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
                    except ValueError:
                        timestamp_dt = datetime.now(timezone.utc)
                else:
                    timestamp_dt = datetime.now(timezone.utc)

                text_content = msg.get("text") or msg.get("content", "")

                formatted_msg = {
                    "role": msg.get("role"),
                    "type": msg.get("type", "conversation_text"),
                    "content": msg.get("content", text_content),
                    "text": text_content,
                    "timestamp": timestamp_dt,
                }
                formatted_messages.append(formatted_msg)

            # Bulk update: add all buffered messages at once
            await self.sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$push": {"messages": {"$each": formatted_messages}},
                    "$set": {"updatedAt": datetime.now(timezone.utc)}
                },
                upsert=True,
            )
            print(f"✅ Stored {len(formatted_messages)} conversation messages for session {session_id}")

        except Exception as exc:
            print(f"❌ Failed to store conversation buffer for session '{session_id}': {exc}")

    async def get_recent_conversations(self, limit: int = 5):
        """Get the most recent conversation(s) from the database"""
        await self.ensure_db()
        if self.sessions_collection is None:
            print(f"⚠️ Cannot get conversations: collection is None")
            return None

        try:
            # Get recent conversations sorted by creation time
            cursor = self.sessions_collection.find().sort("createdAt", -1).limit(limit)
            conversations = await cursor.to_list(length=limit)

            if conversations:
                formatted_conversations = []
                for conv in conversations:
                    serialised = self._serialise_for_client(conv)
                    formatted_conversations.append(serialised)

                print(f"✅ Retrieved {len(formatted_conversations)} conversation(s)")
                return formatted_conversations
            else:
                print("📋 No conversations found in database")
                return None

        except Exception as exc:
            print(f"❌ Failed to get recent conversations: {exc}")
            return None

    async def register_mobile_client(self, websocket):
        """Register a new mobile client"""
        self.mobile_clients.add(websocket)
        print(f"Mobile client connected. Total clients: {len(self.mobile_clients)}")
        print(f"Client address: {websocket.remote_address}")
        
        # Send connection confirmation directly to this client
        connection_msg = {
            "event": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Dr. Claude AI"
        }
        await websocket.send(json.dumps(connection_msg))
        print(f"Sent connection confirmation to mobile client")

        if self.session_metadata:
            await websocket.send(
                json.dumps(
                    {
                        "event": "active_sessions",
                        "sessions": [
                            {
                                "session_id": session_id,
                                "phone_number": meta.get("phone_number"),
                                "username": meta.get("username"),
                                "passcode": meta.get("passcode"),
                            }
                            for session_id, meta in self.session_metadata.items()
                        ],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

    async def unregister_mobile_client(self, websocket):
        """Unregister a mobile client"""
        self.mobile_clients.discard(websocket)
        print(f"Mobile client disconnected. Total clients: {len(self.mobile_clients)}")

    async def send_to_mobile(self, message):
        """Send message to all connected mobile clients"""
        if self.mobile_clients:
            # Send to all connected mobile clients
            disconnected = set()
            for client in self.mobile_clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.mobile_clients.discard(client)

    async def handle_transcription(self, text, is_final=False, session_id: Optional[str] = None):
        """Handle transcription from Deepgram"""
        print(f"Transcription received: '{text}' (final: {is_final})")
        
        transcription = {
            "event": "transcription",
            "text": text,
            "is_final": is_final,
            "timestamp": datetime.now().isoformat()
        }
        
        self.transcriptions.append(transcription)
        await self.send_to_mobile(transcription)
        await self._append_message(
            session_id,
            {
                "role": "user",
                "type": "transcription",
                "text": text,
                "isFinal": is_final,
            },
        )
        print(f"Sent transcription to {len(self.mobile_clients)} mobile clients")

    async def handle_agent_response(self, response_text, session_id: Optional[str] = None):
        """Handle response from the agent"""
        response = {
            "event": "agent_response", 
            "text": response_text,
            "timestamp": datetime.now().isoformat()
        }
        
        self.agent_responses.append(response)
        await self.send_to_mobile(response)
        await self._append_message(
            session_id,
            {
                "role": "assistant",
                "type": "agent_response",
                "text": response_text,
            },
        )

    async def handle_function_call(
        self,
        function_name,
        parameters,
        result,
        session_id: Optional[str] = None,
    ):
        """Handle function call execution"""
        function_call = {
            "event": "function_call",
            "function_name": function_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.function_calls.append(function_call)
        await self.send_to_mobile(function_call)
        await self._append_function_call(
            session_id,
            {
                "name": function_name,
                "parameters": parameters,
                "result": result,
            },
        )

    async def handle_audio_chunk(self, audio_data, duration):
        """Handle audio chunk from mobile app"""
        try:
            print(f"Received audio data: {len(audio_data)} chars, duration: {duration}ms")
            
            # For demo purposes, simulate transcription based on duration
            # In a real implementation, you'd decode actual audio and send to Deepgram
            
            # Only send transcription once per recording session after 2 seconds
            if duration > 2000 and not getattr(self, '_transcription_sent', False):
                self._transcription_sent = True  # Only send once per recording session
                print(f"Triggering simulated transcription (first time for this session)")
                
                simulated_transcript = "Hello, I'm speaking to the doctor assistant"
                print(f"Simulated transcription: '{simulated_transcript}'")
                await self.handle_transcription(simulated_transcript, is_final=True)
                
                # Simulate agent response
                simulated_response = "Hello! I'm Dr. Claude AI. How can I help you with your health today?"
                print(f"Simulated agent response: '{simulated_response}'")
                await self.handle_agent_response(simulated_response)
            elif duration > 2000:
                print(f"Skipping transcription (already sent for this session)")
                
        except Exception as e:
            print(f"Error processing audio chunk: {e}")

    async def handle_user_message(self, message, session_id: Optional[str] = None):
        """Handle text message from user and generate medical response"""
        try:
            print(f"Processing user message: '{message}'")

            # Simple medical response based on keywords
            response = self.generate_medical_response(message)

            print(f"Generated response: '{response}'")
            await self._append_message(
                session_id,
                {
                    "role": "user",
                    "type": "text_message",
                    "text": message,
                },
            )
            await self.handle_agent_response(response, session_id=session_id)

            # Check if we should call any medical functions
            await self.check_for_function_calls(message, session_id=session_id)

        except Exception as e:
            print(f"Error processing user message: {e}")

    def generate_medical_response(self, message):
        """Generate simple medical responses based on keywords"""
        message_lower = message.lower()
        
        # Medical responses - more comprehensive keyword matching
        if any(word in message_lower for word in ['headache', 'head pain', 'migraine', 'head hurt', 'head ache']):
            return "I understand you're experiencing head pain. This could be caused by tension, dehydration, or stress. I recommend rest, hydration, and if it persists, please consult a healthcare provider. Would you like me to schedule an appointment or provide more information about headache management?"
            
        elif any(word in message_lower for word in ['dizzy', 'dizziness', 'dizzy ness', 'light headed', 'lightheaded', 'spinning', 'vertigo']):
            return "Dizziness can have several causes including dehydration, low blood pressure, inner ear problems, or medication side effects. Try sitting or lying down, stay hydrated, and avoid sudden movements. If dizziness is severe, persistent, or accompanied by chest pain or difficulty breathing, seek immediate medical attention. Would you like me to schedule an appointment for evaluation?"
            
        elif any(word in message_lower for word in ['sleep', 'sleeping', 'insomnia', 'can\'t sleep', 'cant sleep', 'not sleeping', 'trouble sleeping', 'getting sleep']):
            return "Sleep problems are common and can affect your overall health. Here are some tips: maintain a regular sleep schedule, avoid caffeine late in the day, create a relaxing bedtime routine, keep your bedroom cool and dark, and limit screen time before bed. If sleep problems persist for more than 2 weeks, consider seeing a healthcare provider. Would you like more specific sleep hygiene tips?"
            
        elif any(word in message_lower for word in ['fever', 'temperature', 'hot', 'chills', 'feverish']):
            return "Fever can indicate your body is fighting an infection. Monitor your temperature, stay hydrated, and get rest. If your fever is over 101°F (38.3°C) or persists for more than 3 days, please seek medical attention. Would you like tips on managing fever?"
            
        elif any(word in message_lower for word in ['cough', 'coughing', 'throat', 'sore throat', 'throat pain']):
            return "A cough can be caused by various factors including cold, flu, or allergies. Try warm liquids, honey, and avoid irritants. If the cough persists for more than 2 weeks or includes blood, please see a healthcare provider. Would you like information about cough remedies?"
            
        elif any(word in message_lower for word in ['chest pain', 'chest hurt', 'heart pain', 'heart hurt']):
            return "Chest pain can be serious. If you're experiencing severe chest pain, shortness of breath, or pain radiating to your arm or jaw, call 911 immediately. For mild chest discomfort, it could be muscle strain or acid reflux, but it's important to get evaluated by a healthcare provider."
            
        elif any(word in message_lower for word in ['anxiety', 'anxious', 'worried', 'stress', 'stressed', 'panic', 'nervous']):
            return "I understand you're feeling anxious. Anxiety is common and treatable. Try deep breathing, meditation, or talking to someone you trust. Regular exercise and good sleep also help. If anxiety interferes with daily life, consider speaking with a mental health professional. Would you like some relaxation techniques?"
            
        elif any(word in message_lower for word in ['stomach', 'stomach pain', 'belly', 'nausea', 'vomit', 'sick', 'stomach ache']):
            return "Stomach discomfort can be caused by many things including food, stress, or viral infections. Try eating bland foods, staying hydrated, and resting. If you have severe pain, persistent vomiting, or signs of dehydration, seek medical attention. Would you like dietary recommendations for stomach upset?"
            
        elif any(word in message_lower for word in ['back pain', 'back hurt', 'spine', 'lower back']):
            return "Back pain is very common and often improves with rest, gentle movement, and over-the-counter pain relievers. Apply heat or ice, try gentle stretching, and avoid bed rest for extended periods. If pain is severe, persists more than a few days, or you have numbness/tingling, see a healthcare provider."
            
        elif any(word in message_lower for word in ['appointment', 'schedule', 'book', 'see doctor', 'visit']):
            return "I can help you schedule an appointment. What type of appointment would you like? A general checkup, follow-up visit, or for a specific concern? Please provide your name and preferred time."
            
        elif any(word in message_lower for word in ['medication', 'medicine', 'drug', 'pill', 'prescription']):
            return "I can provide information about medications. Which medication would you like to know about? Please remember that this information is for educational purposes only, and you should always consult with a healthcare provider or pharmacist about your medications."
            
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return "Hello! I'm Dr. Claude AI, your medical assistant. I can help with symptom assessment, medication information, appointment scheduling, and health tips. Please remember that I provide general information only and am not a substitute for professional medical advice. How can I help you today?"
            
        else:
            return "Thank you for your message. I'm here to help with medical questions, symptom assessment, medication information, and appointment scheduling. Could you please provide more details about what you'd like assistance with? Remember, for emergencies, please call 911."

    async def check_for_function_calls(self, message, session_id: Optional[str] = None):
        """Check if we should call any medical functions based on the message"""
        message_lower = message.lower()
        
        # Simulate function calls based on message content
        if any(word in message_lower for word in ['schedule', 'appointment', 'book']):
            # Simulate scheduling an appointment
            await self.handle_function_call(
                'schedule_appointment',
                {'patient_name': 'User', 'reason': 'general consultation'},
                {'appointment_id': 1, 'message': 'Appointment scheduled for tomorrow at 10:00 AM', 'date': 'Tomorrow 10:00 AM'},
                session_id=session_id
            )
        
        elif any(word in message_lower for word in ['headache', 'fever', 'cough', 'pain', 'dizzy', 'dizziness', 'sleep', 'anxiety', 'stomach', 'back']):
            # Simulate symptom assessment
            symptoms_found = [word for word in ['headache', 'fever', 'cough', 'pain', 'dizziness', 'sleep problems', 'anxiety', 'stomach pain', 'back pain'] if any(s in message_lower for s in [word.replace(' ', ''), word.replace(' problems', ''), word.replace(' pain', '')])]
            symptoms = symptoms_found[0] if symptoms_found else 'general discomfort'
            
            await self.handle_function_call(
                'assess_symptoms',
                {'symptoms': symptoms},
                {'patient_symptoms': symptoms, 'possible_conditions': [{'condition': f'Related to {symptoms}', 'recommendations': ['rest', 'hydration', 'monitor symptoms', 'consult healthcare provider if persists']}]},
                session_id=session_id
            )

    async def mobile_websocket_handler(self, websocket):
        """Handle WebSocket connections from mobile app"""
        await self.register_mobile_client(websocket)
        try:
            # Send initial connection message
            await websocket.send(json.dumps({
                "event": "connection_established",
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to Pharmacy Agent"
            }))
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Handle commands from mobile app if needed
                    command = data.get("command")

                    if command in {"get_history", "fetch_history"}:
                        phone_number = data.get("phone_number")
                        passcode = data.get("passcode")
                        session_id = data.get("session_id")

                        if not phone_number or not passcode:
                            await websocket.send(
                                json.dumps(
                                    {
                                        "event": "history_error",
                                        "message": "phone_number and passcode are required",
                                    }
                                )
                            )
                            continue

                        history_doc = await self.fetch_history(
                            phone_number=phone_number,
                            passcode=passcode,
                            session_id=session_id,
                        )

                        if not history_doc:
                            await websocket.send(
                                json.dumps(
                                    {
                                        "event": "history_error",
                                        "message": "No matching conversation found",
                                    }
                                )
                            )
                            continue

                        history_payload = self._serialise_for_client(history_doc)
                        history_payload.pop("_id", None)

                        await websocket.send(
                            json.dumps(
                                {
                                    "event": "history",
                                    "history": history_payload,
                                }
                            )
                        )

                    elif command in {"set_credentials", "update_credentials"}:
                        session_id = data.get("session_id")
                        username = data.get("username")
                        passcode = data.get("passcode")

                        success, message_text = await self.update_session_credentials(
                            session_id,
                            username=username,
                            passcode=passcode,
                        )

                        await websocket.send(
                            json.dumps(
                                {
                                    "event": "credentials_updated" if success else "credentials_error",
                                    "session_id": session_id,
                                    "message": message_text,
                                }
                            )
                        )

                    elif command == "get_recent_conversations":
                        print(f"🔍 Getting recent conversations from database...")
                        recent_conversations = await self.get_recent_conversations(limit=5)

                        if recent_conversations:
                            print(f"📋 Found {len(recent_conversations)} recent conversations")
                            await websocket.send(
                                json.dumps(
                                    {
                                        "event": "recent_conversations",
                                        "conversations": recent_conversations,
                                    }
                                )
                            )
                        else:
                            print(f"📋 No recent conversations found")
                            await websocket.send(
                                json.dumps(
                                    {
                                        "event": "recent_conversations_error",
                                        "message": "No recent conversations found"
                                    }
                                )
                            )

                    elif command == "ping":
                        await websocket.send(json.dumps({"event": "pong"}))
                        print(f"Ping received from mobile client")
                    elif data.get("event") == "user_message":
                        message = data.get("message", "")
                        session_id = data.get("session_id")
                        print(f"Received user message: '{message}'")
                        await self.handle_user_message(message, session_id=session_id)
                    else:
                        print(f"Received message from mobile: {data}")
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON from mobile client: {message}")
                    error = {"event": "error", "message": "Invalid JSON"}
                    await websocket.send(json.dumps(error))
                except Exception as e:
                    print(f"Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Mobile client connection closed")
        except Exception as e:
            print(f"Error in mobile websocket handler: {e}")
        finally:
            await self.unregister_mobile_client(websocket)

# Global mobile bridge instance
mobile_bridge = MobileBridge()

async def mobile_websocket_handler_wrapper(websocket):
    """Wrapper for the mobile websocket handler"""
    await mobile_bridge.mobile_websocket_handler(websocket)

async def start_mobile_server(*, host: str = "0.0.0.0", port: int = 8080):
    """Start the mobile WebSocket server"""
    print(f"Starting mobile WebSocket server on {host}:{port}...")
    await mobile_bridge.ensure_db()
    return await websockets.serve(
        mobile_websocket_handler_wrapper,
        host,
        port,
        max_size=None
    )
