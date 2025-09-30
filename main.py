
import asyncio
import base64
import json
import ssl
import websockets
import os
from datetime import datetime
from medical_functions import FUNCTION_MAP
from mobile_bridge import mobile_bridge, start_mobile_server
from dotenv import load_dotenv

load_dotenv()

def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("Api key not available")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token",api_key],
        ssl=ssl_context
    )

    return sts_ws


def load_config():
    with open('config.json','r') as f:
        return json.load(f)


async def handle_barge_in(decoded,twilio_ws,streamsid):
    if decoded['type'] == 'UserStatedSpeaking':
        clear_message = {
            'event':'clear',
            'streamSid':streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))


def execute_function_call(func_name,arguments):
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**arguments)
        print(f'function called if {result}')
        return result
    else:
        result = {'error': f'Function {func_name} not found'}
        print(result)
        return result

def create_function_call_response(func_id,fund_name,result):
    return {
            'type':'FunctionCallResponse',
            'id':func_id,
            'name':fund_name,
            'content':json.dumps(result)
    }


async def handle_function_call_request(decoded,sts_ws,session_id):
    try:

        for function_call in decoded['functions']:
            func_name = function_call['name']
            func_id = function_call['id']
            arguments = json.loads(function_call['arguments'])

            print(f'function called : {func_name} {func_id} {arguments}')

            result = execute_function_call(func_name,arguments) 
            function_result = create_function_call_response(func_id,func_name,result)

            await sts_ws.send(json.dumps(function_result))
            print(f'sending the function result :{function_result}')
            
            # Send to mobile app
            await mobile_bridge.handle_function_call(
                func_name,
                arguments,
                result,
                session_id=session_id
            )
    except Exception as e:
        print(f'error {e}')
        error_result = create_function_call_response(
            func_id if 'func_id' in locals() else 'unknown',
            func_name if 'func_name' in locals() else 'unknown',
            {'error':f'func called failed:{str(e)}'}
        )
        await sts_ws.send(json.dumps(error_result))
   

async def handle_text_message(decoded,twilio_ws,sts_ws,streamsid):
    await handle_barge_in(decoded,twilio_ws,streamsid)

    # checking if deepgram require function call or not

    if decoded['type'] == 'FunctionCallRequest':
        await handle_function_call_request(decoded,sts_ws,streamsid)



async def sts_sender(sts_ws,audio_queue):
    print('sts sender started')
    while True:
        chunk = await audio_queue.get() #sending the audio to the twilio after it gets filled to audio_queue in twilio_reveiver
        await sts_ws.send(chunk)


async def sts_receiver(sts_ws,twilio_ws,streamsid_queue):#receive everything from deepgram
    print('sts receiver started') #reveiving from deep gram and sending to twilio
    streamsid = await streamsid_queue.get()

    # Message buffer for storing conversation during call
    conversation_buffer = []

    async for message in sts_ws:
        if type(message) is str:
            decoded = json.loads(message)
            
            # Filter out unwanted message types to reduce noise
            message_type = decoded.get('type', '')
            if message_type in ['History', 'Metadata', 'AgentThinking']:
                continue  # Skip these message types
                
            print(f"Deepgram message: {message}")
            
            # Send transcription to mobile app
            if decoded.get('type') == 'UtteranceEnd':
                transcript = decoded.get('speech_final', '')
                if transcript:
                    print(f"🗣️ Final transcript: '{transcript}'")
                    await mobile_bridge.handle_transcription(
                        transcript,
                        is_final=True,
                        session_id=streamsid
                    )
                else:
                    print(f"⚠️ UtteranceEnd received but no transcript found: {decoded}")
            elif decoded.get('type') == 'SpeechStarted':
                print(f"User started speaking")
                await mobile_bridge.handle_transcription(
                    "User started speaking...",
                    is_final=False,
                    session_id=streamsid
                )
            
            # Send agent responses to mobile app
            if decoded.get('type') == 'AgentAudioDone':
                response_text = decoded.get('text', '')
                if response_text:
                    print(f"Agent response: '{response_text}'")
                    await mobile_bridge.handle_agent_response(
                        response_text,
                        session_id=streamsid
                    )

            # Capture conversation text messages for database storage
            if decoded.get('type') == 'ConversationText':
                role = decoded.get('role', '')
                content = decoded.get('content', '')
                if content and role:
                    print(f"💬 Buffering {role} message: '{content[:50]}...'")
                    conversation_buffer.append({
                        'role': role,
                        'content': content,
                        'timestamp': datetime.now().isoformat()
                    })
            
            await handle_text_message(decoded,twilio_ws,sts_ws,streamsid)
            continue

        raw_mulaw = message

        media_message = {#this is to send twilio
            "event":"media",
            "streamSid":streamsid,
            "media":{"payload":base64.b64encode(raw_mulaw).decode('ascii')}
        }

        await twilio_ws.send(json.dumps(media_message))

    # Store buffered conversation to MongoDB when call ends
    if conversation_buffer:
        print(f"💾 Storing {len(conversation_buffer)} messages to MongoDB for session {streamsid}")
        await mobile_bridge.store_conversation_buffer(streamsid, conversation_buffer)
        conversation_buffer.clear()
        print("✅ Conversation buffer stored and cleared")

async def twilio_receiver(twilio_ws,audio_queue,streamsid_queue):
    BUFFER_SIZE = 20*160 #how much audio we want to store befour sending this to twilio 
    inbuffer = bytearray(b"")
    current_streamsid = None

    async for message in twilio_ws:
        try:
            data = json.loads(message)#loading it to data
            event = data['event']

            if event == 'start':
                print('📞 Twilio call started - getting stream ID')
                start = data['start']
                streamsid = start['streamSid']
                current_streamsid = streamsid
                print(f"🔗 Stream ID: {streamsid}")
                streamsid_queue.put_nowait(streamsid) #
                await mobile_bridge.start_session(streamsid, start)

            elif event == 'connected':
                continue

            elif event == 'media':
                media = data['media']
                chunk = base64.b64decode(media['payload'])
                if media['track'] == 'inbound':
                    # print(f"📢 Received audio chunk: {len(chunk)} bytes")
                    inbuffer.extend(chunk)

                    while len(inbuffer) >= BUFFER_SIZE:#limiting the audio before we sending it to deepgram
                        chunk = inbuffer[:BUFFER_SIZE]
                        # print(f"🎤 Sending audio to Deepgram: {len(chunk)} bytes")
                        audio_queue.put_nowait(chunk)
                        inbuffer = inbuffer[BUFFER_SIZE:]

            elif event == 'stop':
                session_to_close = data.get('streamSid') or current_streamsid
                if session_to_close:
                    await mobile_bridge.end_session(session_to_close)
                break
        except Exception as e:
            print(f"⚠️ Error processing Twilio message: {e}")
            break





async def twilio_handler(twilio_ws):
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()

    try:
        async with sts_connect() as sts_ws:
            config_message = load_config()
            await sts_ws.send(json.dumps(config_message)) #sending the config message to the deep gram

            tasks = [
                asyncio.create_task(sts_sender(sts_ws,audio_queue)),
                asyncio.create_task(sts_receiver(sts_ws,twilio_ws,streamsid_queue)),
                asyncio.create_task(twilio_receiver(twilio_ws,audio_queue,streamsid_queue)),
            ]

            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
            
            # Check for exceptions in completed tasks
            for task in done:
                if task.exception():
                    raise task.exception()
    except Exception as e:
        print(f"⚠️ Connection handler failed: {e}")
        print(f"🔄 This is normal when calls end - reconnection will happen automatically")
    finally:
        try:
            await twilio_ws.close()
        except:
            pass


async def main():
    twilio_port = int(os.getenv('TWILIO_WS_PORT', '5000'))
    mobile_port = int(os.getenv('MOBILE_WS_PORT', '8080'))

    print(f'Twilio server binding to port {twilio_port}')
    twilio_server = await websockets.serve(twilio_handler,'localhost',twilio_port)

    print(f'Mobile server binding to port {mobile_port}')
    mobile_server = await start_mobile_server(host='0.0.0.0', port=mobile_port)
    
    print(f'Twilio server started on port {twilio_port}')
    print(f'Mobile WebSocket server started on port {mobile_port}')
    print('Pharmacy Assistant is ready!')
    
    # Keep both servers running
    await asyncio.gather(
        twilio_server.wait_closed(),
        mobile_server.wait_closed()
    )


if __name__ == '__main__':
    asyncio.run(main())


