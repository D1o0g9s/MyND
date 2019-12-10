# WS server example

import asyncio
import websockets
import json

from pylsl import StreamInfo, StreamOutlet

info = StreamInfo(name='eyeTracker', type='eye',channel_count=2, nominal_srate=0, channel_format='int32',source_id='eyeTrackerSocket_Server')
outlet = StreamOutlet(info)

info_n = StreamInfo(name='eyeTrackerNorm', type='eyeNorm',channel_count=2, nominal_srate=0, channel_format='float32', source_id='eyeTrackerSocket_Server_Norm')
outlet_n = StreamOutlet(info_n)


async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    while(True) :
        eyeLocation = await websocket.recv()
        eyeLocation = json.loads(eyeLocation)
        print("x:", eyeLocation["x"], "y:",  eyeLocation["y"], "x_norm:", eyeLocation["x_norm"], "y_norm:", eyeLocation["y_norm"])
        eyeLocation_coord = [eyeLocation["x"], eyeLocation["y"]]
        outlet.push_sample(eyeLocation_coord)
        outlet_n.push_sample([eyeLocation["x_norm"], eyeLocation["y_norm"]])

start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
