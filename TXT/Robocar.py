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
    'M1':  TXT_M_M1_encodermotor,
    'M2':  TXT_M_M2_encodermotor,
    'M3':  TXT_M_M3_encodermotor,
    'M4':  TXT_M_M4_encodermotor,
    'CW':  Motor.CW,
    'CCW': Motor.CCW,
}

state.motors_dict = motors_dict
state.dist_sensor_dict = dist_sensor_dict

trail_sensors_dict = {
    'left':  TXT_M_I7_trail_follower,
    'right': TXT_M_I8_trail_follower,
}

dist_sensor_dict = {
    'front' : TXT_M_I2_ultrasonic_distance_meter,
    'left' : TXT_M_I3_ultrasonic_distance_meter,
    'right' : TXT_M_I4_ultrasonic_distance_meter

}


client = connect_mqtt()
client.loop_start()

def sensor_loop():
    from mqtt_handlers import publish_sensors
    while True:
        try:
            if state.mqtt_client and state.CLIENT_ID:
                publish_sensors(state.mqtt_client, state.CAR_ID)
        except Exception as e:
            print("sensor_loop error:", e)
        time.sleep(0.2)

threading.Thread(target=sensor_loop, daemon=True).start()

COMMAND_MAP = {
    "follow_line":   lambda: commands.run_follow_line(motors_dict, trail_sensors_dict),
    "follow_wall":   lambda: commands.run_follow_wall(motors_dict, dist_sensor_dict),
    "avoid_topdown": lambda: commands.run_avoid_topdown(motors_dict, dist_sensor_dict),
    "braitenberg":   lambda: commands.run_braitenberg(motors_dict, dist_sensor_dict),
    "move_forward":  lambda: commands.move_for_seconds(commands.move_forward,motors_dict, 10, speed=260),
    "move_backward": lambda: commands.move_for_seconds(commands.move_backward,motors_dict, 10, speed=260),
    "strafe_right":lambda: commands.move_for_seconds(commands.strafe_right,motors_dict, 10, speed=260),
    "strafe_left":lambda: commands.move_for_seconds(commands.strafe_left,motors_dict, 10, speed=260),
    "rotate_cw":lambda: commands.move_for_seconds(commands.rotate_cw,motors_dict, 1.0, speed=200),
    "rotate_ccw":lambda: commands.move_for_seconds(commands.rotate_ccw,motors_dict, 1.0, speed=200),
    "diagonal_front_right":lambda: commands.move_for_seconds(commands.move_diagonal_front_right, motors_dict, 10, speed=260),
    "diagonal_front_left":lambda: commands.move_for_seconds(commands.move_diagonal_front_left,  motors_dict, 10, speed=260),
    "diagonal_rear_right":lambda: commands.move_for_seconds(commands.move_diagonal_rear_right,  motors_dict, 10, speed=260),
    "diagonal_rear_left":lambda: commands.move_for_seconds(commands.move_diagonal_rear_left,   motors_dict, 10, speed=260),
    "arc_right_gentle":lambda: commands.move_for_seconds(commands.arc_turn_right,motors_dict, 10, speed=260, turn_ratio=0.3),
    "arc_left_gentle":lambda: commands.move_for_seconds(commands.arc_turn_left,motors_dict, 10, speed=260, turn_ratio=0.3),
    "arc_right_sharp":lambda: commands.move_for_seconds(commands.arc_turn_right,motors_dict, 10, speed=260, turn_ratio=0.7),
    "arc_left_sharp":lambda: commands.move_for_seconds(commands.arc_turn_left,motors_dict, 10, speed=260, turn_ratio=0.7),
}



TXT_M_USB1_1_camera.set_rotate(False)
TXT_M_USB1_1_camera.set_height(240)
TXT_M_USB1_1_camera.set_width(320)
TXT_M_USB1_1_camera.set_fps(30)
TXT_M_USB1_1_camera.start()

services.camera_stream = CameraStreamServer(TXT_M_USB1_1_camera)

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


def pause():
    time.sleep(0.2)


# print("=== Cardinal directions ===")

# print("Forward")
# commands.move_for_seconds(commands.move_forward,  motors_dict, 10, speed=260)
# pause()

# print("Backward")
# commands.move_for_seconds(commands.move_backward, motors_dict, 10, speed=260)
# pause()

# print("Strafe right")
# commands.move_for_seconds(commands.strafe_right,  motors_dict, 10, speed=260)
# pause()

# print("Strafe left")
# commands.move_for_seconds(commands.strafe_left,   motors_dict, 10, speed=260)
# pause()

# # ── 2. Rotations ──────────────────────────────────────────────────────────────
# print("=== Rotations ===")

# print("Rotate CW")
# commands.move_for_seconds(commands.rotate_cw,  motors_dict, 1.0, speed=200)
# pause()

# print("Rotate CCW")
# commands.move_for_seconds(commands.rotate_ccw, motors_dict, 1.0, speed=200)
# pause()

# # ── 3. Diagonals ──────────────────────────────────────────────────────────────
# print("=== Diagonals ===")

# print("Diagonal front-right")
# commands.move_for_seconds(commands.move_diagonal_front_right, motors_dict, 10, speed=260)
# pause()

# print("Diagonal front-left")
# commands.move_for_seconds(commands.move_diagonal_front_left,  motors_dict, 10, speed=260)
# pause()

# print("Diagonal rear-right")
# commands.move_for_seconds(commands.move_diagonal_rear_right,  motors_dict, 10, speed=260)
# pause()

# print("Diagonal rear-left")
# commands.move_for_seconds(commands.move_diagonal_rear_left,   motors_dict, 10, speed=260)
# pause()

# # ── 4. Arc turns ──────────────────────────────────────────────────────────────
# print("=== Arc turns ===")

# print("Arc turn right (gentle, ratio=0.3)")
# commands.move_for_seconds(commands.arc_turn_right, motors_dict, 10, speed=260, turn_ratio=0.3)
# pause()

# print("Arc turn left (gentle, ratio=0.3)")
# commands.move_for_seconds(commands.arc_turn_left,  motors_dict, 10, speed=260, turn_ratio=0.3)
# pause()

# print("Arc turn right (sharp, ratio=0.7)")
# commands.move_for_seconds(commands.arc_turn_right, motors_dict, 10, speed=260, turn_ratio=0.7)
# pause()

# print("Arc turn left (sharp, ratio=0.7)")
# commands.move_for_seconds(commands.arc_turn_left,  motors_dict, 10, speed=260, turn_ratio=0.7)
# pause()

# # ── 10. Speed ramp ─────────────────────────────────────────────────────────────
# print("=== Speed ramp (forward) ===")

# for spd in [100, 200, 300, 400, 1012]:
#     print("  Forward speed={}".format(spd))
#     commands.move_for_seconds(commands.move_forward, motors_dict, 0.8, speed=spd)
#     pause()

# # ── 6. Square pattern ─────────────────────────────────────────────────────────
# print("=== Square pattern ===")

# square_moves = [
#     ("Forward",      commands.move_forward),
#     ("Strafe right", commands.strafe_right),
#     ("Backward",     commands.move_backward),
#     ("Strafe left",  commands.strafe_left),
# ]

# for label, fn in square_moves:
#     print("  {}".format(label))
#     commands.move_for_seconds(fn, motors_dict, 10, speed=260)
#     pause()

# # ── 7. X pattern (diagonals) ──────────────────────────────────────────────────
# print("=== X diagonal pattern ===")

# diagonal_moves = [
#     ("Front-right", commands.move_diagonal_front_right),
#     ("Rear-left",   commands.move_diagonal_rear_left),
#     ("Front-left",  commands.move_diagonal_front_left),
#     ("Rear-right",  commands.move_diagonal_rear_right),
# ]

# for label, fn in diagonal_moves:
#     print("  {}".format(label))
#     commands.move_for_seconds(fn, motors_dict, 1.0, speed=260)
#     pause()

# # ── 8. Spin test ──────────────────────────────────────────────────────────────
# print("=== Full spin (CW then CCW) ===")

# print("  CW full rotation (~2s)")
# commands.move_for_seconds(commands.rotate_cw,  motors_dict, 2.0, speed=260)
# pause()

# print("  CCW full rotation (~2s)")
# commands.move_for_seconds(commands.rotate_ccw, motors_dict, 2.0, speed=260)
# pause()

# print("=== All tests complete ===")

#commands.run_follow_wall(motors_dict, dist_sensor_dict)
#commands.run_braitenberg(motors_dict, dist_sensor_dict)
#commands.run_avoid_topdown(motors_dict, dist_sensor_dict)
#commands.run_follow_line(motors_dict, trail_sensors_dict)
