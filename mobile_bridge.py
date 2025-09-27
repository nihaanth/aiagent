import asyncio
import json
import websockets
from datetime import datetime

class MobileBridge:
    def __init__(self):
        self.mobile_clients = set()
        self.transcriptions = []
        self.agent_responses = []
        self.function_calls = []

    async def register_mobile_client(self, websocket):
        """Register a new mobile client"""
        self.mobile_clients.add(websocket)
        print(f"🔗 Mobile client connected. Total clients: {len(self.mobile_clients)}")
        print(f"📱 Client address: {websocket.remote_address}")
        
        # Send connection confirmation directly to this client
        connection_msg = {
            "event": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Dr. Claude AI"
        }
        await websocket.send(json.dumps(connection_msg))
        print(f"✅ Sent connection confirmation to mobile client")

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

    async def handle_transcription(self, text, is_final=False):
        """Handle transcription from Deepgram"""
        print(f"🎙️ Transcription received: '{text}' (final: {is_final})")
        
        transcription = {
            "event": "transcription",
            "text": text,
            "is_final": is_final,
            "timestamp": datetime.now().isoformat()
        }
        
        self.transcriptions.append(transcription)
        await self.send_to_mobile(transcription)
        print(f"📱 Sent transcription to {len(self.mobile_clients)} mobile clients")

    async def handle_agent_response(self, response_text):
        """Handle response from the agent"""
        response = {
            "event": "agent_response", 
            "text": response_text,
            "timestamp": datetime.now().isoformat()
        }
        
        self.agent_responses.append(response)
        await self.send_to_mobile(response)

    async def handle_function_call(self, function_name, parameters, result):
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

    async def handle_audio_chunk(self, audio_data, duration):
        """Handle audio chunk from mobile app"""
        try:
            print(f"🎧 Received audio data: {len(audio_data)} chars, duration: {duration}ms")
            
            # For demo purposes, simulate transcription based on duration
            # In a real implementation, you'd decode actual audio and send to Deepgram
            
            # Only send transcription once per recording session after 2 seconds
            if duration > 2000 and not getattr(self, '_transcription_sent', False):
                self._transcription_sent = True  # Only send once per recording session
                print(f"🎯 Triggering simulated transcription (first time for this session)")
                
                simulated_transcript = "Hello, I'm speaking to the doctor assistant"
                print(f"🤖 Simulated transcription: '{simulated_transcript}'")
                await self.handle_transcription(simulated_transcript, is_final=True)
                
                # Simulate agent response
                simulated_response = "Hello! I'm Dr. Claude AI. How can I help you with your health today?"
                print(f"🤖 Simulated agent response: '{simulated_response}'")
                await self.handle_agent_response(simulated_response)
            elif duration > 2000:
                print(f"🔇 Skipping transcription (already sent for this session)")
                
        except Exception as e:
            print(f"❌ Error processing audio chunk: {e}")

    async def handle_user_message(self, message):
        """Handle text message from user and generate medical response"""
        try:
            print(f"🤖 Processing user message: '{message}'")
            
            # Simple medical response based on keywords
            response = self.generate_medical_response(message)
            
            print(f"🤖 Generated response: '{response}'")
            await self.handle_agent_response(response)
            
            # Check if we should call any medical functions
            await self.check_for_function_calls(message)
            
        except Exception as e:
            print(f"❌ Error processing user message: {e}")

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
            return "⚠️ Chest pain can be serious. If you're experiencing severe chest pain, shortness of breath, or pain radiating to your arm or jaw, call 911 immediately. For mild chest discomfort, it could be muscle strain or acid reflux, but it's important to get evaluated by a healthcare provider."
            
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

    async def check_for_function_calls(self, message):
        """Check if we should call any medical functions based on the message"""
        message_lower = message.lower()
        
        # Simulate function calls based on message content
        if any(word in message_lower for word in ['schedule', 'appointment', 'book']):
            # Simulate scheduling an appointment
            await self.handle_function_call(
                'schedule_appointment',
                {'patient_name': 'User', 'reason': 'general consultation'},
                {'appointment_id': 1, 'message': 'Appointment scheduled for tomorrow at 10:00 AM', 'date': 'Tomorrow 10:00 AM'}
            )
        
        elif any(word in message_lower for word in ['headache', 'fever', 'cough', 'pain', 'dizzy', 'dizziness', 'sleep', 'anxiety', 'stomach', 'back']):
            # Simulate symptom assessment
            symptoms_found = [word for word in ['headache', 'fever', 'cough', 'pain', 'dizziness', 'sleep problems', 'anxiety', 'stomach pain', 'back pain'] if any(s in message_lower for s in [word.replace(' ', ''), word.replace(' problems', ''), word.replace(' pain', '')])]
            symptoms = symptoms_found[0] if symptoms_found else 'general discomfort'
            
            await self.handle_function_call(
                'assess_symptoms',
                {'symptoms': symptoms},
                {'patient_symptoms': symptoms, 'possible_conditions': [{'condition': f'Related to {symptoms}', 'recommendations': ['rest', 'hydration', 'monitor symptoms', 'consult healthcare provider if persists']}]}
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
                    if data.get("command") == "get_history":
                        history = {
                            "event": "history",
                            "transcriptions": self.transcriptions[-10:],  # Last 10
                            "responses": self.agent_responses[-10:],
                            "function_calls": self.function_calls[-10:]
                        }
                        await websocket.send(json.dumps(history))
                    elif data.get("command") == "ping":
                        await websocket.send(json.dumps({"event": "pong"}))
                        print(f"🏓 Ping received from mobile client")
                    elif data.get("event") == "user_message":
                        message = data.get("message", "")
                        print(f"💬 Received user message: '{message}'")
                        await self.handle_user_message(message)
                    else:
                        print(f"📨 Received message from mobile: {data}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from mobile client: {message}")
                    error = {"event": "error", "message": "Invalid JSON"}
                    await websocket.send(json.dumps(error))
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
                    
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

async def start_mobile_server():
    """Start the mobile WebSocket server"""
    print("Starting mobile WebSocket server on port 8080...")
    return await websockets.serve(
        mobile_websocket_handler_wrapper,
        "0.0.0.0", 
        8080,
        max_size=None
    )