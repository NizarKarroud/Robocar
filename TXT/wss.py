from tls import create_ssl_context , get_cert_and_key

import asyncio
import websockets
import base64
import cv2
import numpy as np
from functools import partial
import state
cert_path, key_path , ca_file = get_cert_and_key()

ssl_context = create_ssl_context(cert_path, key_path , ca_file)



async def stream(websocket, path, camera):
    print("Client connected")
   
    try:
        ssl_object = websocket.writer.transport.get_extra_info('ssl_object')
        if ssl_object is None:
            print("Pas de SSL")
            await websocket.close()
            return
            
        cert = ssl_object.getpeercert()

        if not cert:
            print("Pas de certificat client")
            await websocket.close()
            return

        cn = dict(x[0] for x in cert['subject']).get('commonName')

        if cn != state.CLIENT_ID:
            print("CN non autorise: {}".format(cn))
            await websocket.close()
            return

        print("Client autorise: {}".format(cn))
    
        while True:
            result = camera.read()
            if not result:
                await asyncio.sleep(0.01)
                continue

            success, frame, _ = result
            if not success:
                await asyncio.sleep(0.01)
                continue

            frame = np.array(frame, dtype=np.uint8)
            _, jpg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            b64 = base64.b64encode(jpg.tobytes()).decode('utf-8')

            await websocket.send(b64)
            await asyncio.sleep(0.1)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        camera.stop()



def start_wss(camera):
    handler = partial(stream, camera=camera)
    return websockets.serve(
        handler,
        "0.0.0.0",
        8765,
        ssl=ssl_context
    )