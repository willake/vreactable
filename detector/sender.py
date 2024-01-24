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
    data = ""
    if len(markerIds) == 0:
        data = "empty"
    else:
        for id, p, r in zip(markerIds, positions, rotations):
            if id > -1:
                markerId = id[0]

                data += f"Box{markerId}"
                data += f"[{format(p[0])};{format(p[1])};{format(p[2])}]"
                data += f"/"
                data += f"[{format(r[0])};{format(r[1])};{format(-r[2])}]"
                data += f"Box{markerId}end/"

    message = {"raw": data}
    ws.send(json.dumps(message))
    print(data)
