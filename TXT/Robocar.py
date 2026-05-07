from lib.controller import *

import threading
import queue
import time
import wss
import asyncio


TXT_M_USB1_1_camera.set_rotate(False)
TXT_M_USB1_1_camera.set_height(240)
TXT_M_USB1_1_camera.set_width(320)
TXT_M_USB1_1_camera.set_fps(30)
TXT_M_USB1_1_camera.start()


start_server = wss.start_wss(TXT_M_USB1_1_camera)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

# Keep main thread alive

# from lib.mqtt import connect_mqtt

# client = connect_mqtt()
# client.loop_forever()

# from flask import Flask, Response
# import numpy as np
# import cv2
# import sys
# import os 

# from lib.controller import *
# import fischertechnik.factories as txt_factory

# app = Flask(__name__)



# def generate():
#     while True:
#         result = TXT_M_USB1_1_camera.read()
#         if not result:
#             continue

#         success, frame, _ = result
#         if not success:
#             continue

#         frame = np.array(frame, dtype=np.uint8)

#         _, jpeg = cv2.imencode('.jpg', frame)

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' +
#                jpeg.tobytes() + b'\r\n')


# @app.route('/video')
# def video():
#     return Response(generate(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# app.run(host='0.0.0.0', port=5000)    