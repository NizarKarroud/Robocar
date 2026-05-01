from lib.controller import *

import threading
import queue
import time

q = queue.Queue()

def sensor_loop():
    while True:
        distance = TXT_M_I1_ultrasonic_distance_meter.get_distance()
        q.put(distance)
        time.sleep(0.1)  # 100 ms delay

def consumer():
    while True:
        value = q.get()
        print("Received:", value)

# Create threads (non-daemon so program stays alive)
t1 = threading.Thread(target=sensor_loop)
t2 = threading.Thread(target=consumer)

t1.start()
t2.start()

# Keep main thread alive
t1.join()
t2.join()
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

# TXT_M_USB1_1_camera.set_rotate(False)
# TXT_M_USB1_1_camera.set_height(240)
# TXT_M_USB1_1_camera.set_width(320)
# TXT_M_USB1_1_camera.set_fps(80)
# TXT_M_USB1_1_camera.start()


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