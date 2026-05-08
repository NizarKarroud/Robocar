import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "TXT"))

from lib.controller import *

import threading
import queue
import time
import asyncio
from stream import CameraStreamServer
import services
from mqtt import connect_mqtt


TXT_M_USB1_1_camera.set_rotate(False)
TXT_M_USB1_1_camera.set_height(240)
TXT_M_USB1_1_camera.set_width(320)
TXT_M_USB1_1_camera.set_fps(30)
TXT_M_USB1_1_camera.start()



services.camera_stream = CameraStreamServer(
    TXT_M_USB1_1_camera
)
client = connect_mqtt()
client.loop_start()   # ✅ NON-BLOCKING

while True:
    
    time.sleep(1)

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