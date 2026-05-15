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
TXT_M_USB1_1_camera.set_height(480)
TXT_M_USB1_1_camera.set_width(640)

TXT_M_USB1_1_camera.set_fps(30)
TXT_M_USB1_1_camera.start()



services.camera_stream = CameraStreamServer(
    TXT_M_USB1_1_camera
)
client = connect_mqtt()
client.loop_start()   # ✅ NON-BLOCKING

while True:
    
    time.sleep(1)
