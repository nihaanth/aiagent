
import asyncio
import base64
import json
import ssl
import websockets
import os
from pharma_functions import FUNCTION_MAP
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


def execute_function_call(func_name,argunments):
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**argunments)
        print(f'function called if {result}')
        return result
    else:
        result = {'error :{func_name}'}
        print(result)
        return result

def create_function_call_response(func_id,fund_name,result):
    return {
            'type':'FunctionCallResponse',
            'id':func_id,
            'name':fund_name,
            'content':json.dumps(result)
    }


async def handle_function_call_request(decoded,sts_ws):
    try:

        for function_call in decoded['function']:
            func_name = function_call['name']
            func_id = function_call['id']
            arguments = json.loads(function_call['argunments'])

            print(f'function called : {func_name} {func_id} {argunments}')

            result = execute_function_call(func_name,argunments) 
            function_result = create_function_call_response(func_id,func_name,result)

            await sts_ws.send(json.dumps(function_result))
            print(f'sending the function result :{function_results}')
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
        await handle_function_call_request(decided,sts_ws)



async def sts_sender(sts_ws,audio_queue):
    print('sts sender started')
    while True:
        chunk = await audio_queue.get() #sending the audio to the twilio after it gets filled to audio_queue in twilio_reveiver
        await sts_ws.send(chunk)


async def sts_receiver(sts_ws,twilio_ws,streamsid_queue):#receive everything from deepgram
    print('sts receiver started') #reveiving from deep gram and sending to twilio
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        if type(message) is str:
            print(message)
            decoded = json.loads(message)
            await handle_text_message(decoded,twilio_ws,sts_ws,streamsid)
            continue

        raw_mulaw = message

        media_message = {#this is to send twilio
            "event":"media",
            "streamSid":streamsid,
            "media":{"payload":base64.b64encode(raw_mulaw).decode('ascii')}
        }

        await twilio_ws.send(json.dumps(media_message))

async def twilio_receiver(twilio_ws,audio_queue,streamsid_queue):
    BUFFER_SIZE = 20*160 #how much audio we want to store befour sending this to twilio 
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)#loading it to data
            event = data['event']

            if event == 'start':
                print('get the streams id')
                start = data['start']
                streamsid = start['streamSid']
                streamsid_queue.put_nowait(streamsid) #

            elif event == 'connected':
                continue

            elif event == 'media':
                media = data['media']
                chunk = base64.b64decode(media['payload'])
                if media['track'] == 'inbound':
                    inbuffer.extend(chunk)
                    
                    while len(inbuffer) >= BUFFER_SIZE:#limiting the audio before we sending it to deepgram
                        chunk = inbuffer[:BUFFER_SIZE]
                        audio_queue.put_nowait(chunk)
                        inbuffer = inbuffer[BUFFER_SIZE:]

            elif event == 'stop':
                break
        except:
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
        print(f"connection handler failed: {e}")
    finally:
        await twilio_ws.close()


async def main():
    await websockets.serve(twilio_handler,'localhost',5000)
    print('server started')
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())






