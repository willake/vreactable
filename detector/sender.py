import websocket
import json 
import numpy as np
import math

def setup_websocket_client(ip: str):
    ws = websocket.create_connection(ip)
    # ws = websocket.create_connection("ws://10.2.40.112:8080/")
    return ws

def format(v):
    return "{:.0f}".format(round(v, 1))

lastIds = []
def send_object_data(ws: websocket.WebSocket(), markerIds, positions, rotations):
    data = ''
    if len(markerIds) == 0:
        data = 'empty'
    else:
        for id,p,r in zip(markerIds, positions, rotations):
            if id > -1:
                markerId = id[0]
                x = p[0][0]
                y = p[1][0] * -1
                z = p[2][0] 
                
                roll = r[0]
                pitch = r[1]
                yaw = r[2]

                data += f'Box{markerId}'
                data += f'[{format(x)};{format(y)};{format(z)}]'
                data += f'/'
                data += f'[{format(0)};{format(0)};{format(-yaw)}]'
                data += f'Box{markerId}end/'
    
    message = {
        "raw": data
    }
    ws.send(json.dumps(message))
    print(data)