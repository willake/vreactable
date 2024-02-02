import websocket
import json
from helper import helper


class Client:
    def __init__(self, ip: str):
        self.ws = websocket.create_connection(ip)

    def sendCubeData(self, markerIds, positions, rotations):
        data = ""
        if len(markerIds) == 0:
            data = "empty"
        else:
            for id, p, r in zip(markerIds, positions, rotations):
                if id > -1:
                    markerId = id[0]

                    data += f"Box{markerId}"
                    data += f"[{helper.format(p[0][0])};{helper.format(p[1][0])};{helper.format(p[2][0])}]"
                    data += f"/"
                    data += f"[{helper.format(r[0])};{helper.format(r[1])};{helper.format(-r[2])}]"
                    data += f"Box{markerId}end/"

        message = {"raw": data}
        self.ws.send(json.dumps(message))
        print(data)
