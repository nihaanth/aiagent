
import asyncio
import base64
import json
import websockets
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("Api key not available")

    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token",api_key]
    )

    return sts_ws


def load_config():
    with open('config.json','r') as f:
        json.load(f)


async def handle_barge_in(decoded,twilio_ws,streamsid):
    if decoded['type'] == 'UserStatedSpraking'

async def handle_text_message(decoded,twilio_ws,sts_ws,streamsid):
    pass

async def sts_sender(sts_ws,audio_queue):
    print('sts sender started')
    while True:
        chunk = await audio_queue.get() #sending the audio to the twilio after it gets filled to audio_queue in twilio_reveiver
        await sts_ws.send(chunk)


async def sts_receiver(sts_ws,twilio_ws,streamsid_queue):
    print('sts receiver started') #reveiving from deep gram and sending to twilio
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        if type(message) is str:
            print(message)
            decoded = json.loads(message)
            await handle_text_message(decoded,twilio_ws,stramsid)
            continue

        raw_mulaw = message

        media_message = {#this is to send twilio
            "event":"media",
            "streamSid":streamsid,
            "media":{"payload":base64.b64encode(raw_mulaw).decode('ascii')}
        }

        await twilio_ws.send(json.dumps(media_message))

async def twilio_reveiver(twilio_ws,audio_queue,streamsid_queue):
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

            elif event == 'stop':
                break

            while len(inbound) >= BUFFER_SIZE:#limiting the audio before we sending it to deepgram
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.pit_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except:
            break






async def twilio_handler(twilio_ws):
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()

    async with sts_connect() as sts_ws:
        config_message = load_config()
        await sts_ws.send(json.dumps(config_message)) #sending the config message to the deep gram

        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws,audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws,twilio_ws,streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws,audio_queue,streamsid_queue)),

            ]
        )

        await twilio_ws.close()


async def main():
    await websockets.serve(twilio_handler,'localhost',5000)
    print('server started')
    await asyncio.Future()


if __name__ = '__main__':
    asyncio.run(main())






