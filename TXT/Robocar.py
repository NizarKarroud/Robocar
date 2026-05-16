import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "TXT"))

from lib.controller import *
from fischertechnik.controller.Motor import Motor

import time
import threading
import state
import services
import commands
from stream import CameraStreamServer
from mqtt import connect_mqtt

motors_dict = {
    'M1':  AG_M_M1_encodermotor,
    'M2':  AG_M_M2_encodermotor,
    'M3':  AG_M_M3_encodermotor,
    'M4':  AG_M_M4_encodermotor,
    'CW':  Motor.CW,
    'CCW': Motor.CCW,
}

trail_sensors_dict = {
    'left':  AG_M_I7_trail_follower,
    'right': AG_M_I8_trail_follower,
}

COMMAND_MAP = {
    "follow_line": lambda: commands.run_follow_line(motors_dict, trail_sensors_dict),
}

print("before connect_mqtt")
client = connect_mqtt()
print("after connect_mqtt")
client.loop_start()
print("after loop_start")

TXT_M_USB1_1_camera.set_rotate(False)
TXT_M_USB1_1_camera.set_height(240)
TXT_M_USB1_1_camera.set_width(320)
TXT_M_USB1_1_camera.set_fps(30)
TXT_M_USB1_1_camera.start()
print("after camera start")

services.camera_stream = CameraStreamServer(TXT_M_USB1_1_camera)
print("after camera stream")

print("Command executor ready")


while True:
    try:
        command = state.command_queue.get(timeout=1)
    except Exception:
        continue
    
    print(command)
    handler = COMMAND_MAP.get(command)
    if handler:
        t = threading.Thread(target=handler, daemon=True)
        t.start()
        t.join()
    else:
        print("Unknown command:", command)