import time
import state
import math
from datetime import datetime, timezone
from mqtt_handlers import canonical_json

# ── Robot physical parameters ────────────────────────────────────────────────
R  = 2.75
L  = 18.0
W  = 22.6
LX = L / 2
LY = W / 2

def stop_motors(motors_dict):
    m = motors_dict
    m['M1'].set_speed(0, m['CW'])
    m['M2'].set_speed(0, m['CW'])
    m['M3'].set_speed(0, m['CW'])
    m['M4'].set_speed(0, m['CW'])
    m['M1'].stop_sync()
    m['M2'].stop_sync()
    m['M3'].stop_sync()
    m['M4'].stop_sync()

def motors_mecanum(motors_dict, fl, fr, rl, rr):
    M2_BOOST = 30
    m = motors_dict
    fr_boosted = max(-512, min(512, fr + (M2_BOOST if fr >= 0 else -M2_BOOST)))
    m['M1'].set_speed(abs(fl),         m['CW']  if fl         >= 0 else m['CCW'])
    m['M2'].set_speed(abs(fr_boosted), m['CCW'] if fr_boosted >= 0 else m['CW'])
    m['M3'].set_speed(abs(rl),         m['CCW'] if rl         >= 0 else m['CW'])
    m['M4'].set_speed(abs(rr),         m['CCW'] if rr         >= 0 else m['CW'])
    m['M1'].start()
    m['M2'].start()
    m['M3'].start()
    m['M4'].start()

def motors_run(motors_dict, left_speed, right_speed):
    motors_mecanum(motors_dict, left_speed, right_speed, left_speed, right_speed)

def compute_wheel_speeds(vx, vy, omega):
    k = LX + LY
    w1_fr = (1 / R) * ( vx - vy - k * omega)
    w2_fl = (1 / R) * ( vx + vy + k * omega)
    w3_rl = (1 / R) * ( vx - vy + k * omega)
    w4_rr = (1 / R) * ( vx + vy - k * omega)
    return w1_fr, w2_fl, w3_rl, w4_rr

def _scale_to_pwm(wheel_speeds, max_pwm=512):
    max_speed = max(abs(w) for w in wheel_speeds)
    if max_speed == 0:
        return (0, 0, 0, 0)
    scale = max_pwm / max_speed
    return tuple(int(w * scale) for w in wheel_speeds)

def drive(motors_dict, vx, vy, omega, max_pwm=512):
    speeds = compute_wheel_speeds(vx, vy, omega)
    fr, fl, rl, rr = _scale_to_pwm(speeds, max_pwm)
    motors_mecanum(motors_dict, fl, fr, rl, rr)

def move_forward(motors_dict, speed=260):
    drive(motors_dict, vx=speed, vy=0, omega=0)

def move_backward(motors_dict, speed=260):
    drive(motors_dict, vx=-speed, vy=0, omega=0)

def strafe_right(motors_dict, speed=260):
    drive(motors_dict, vx=0, vy=speed, omega=0)

def strafe_left(motors_dict, speed=260):
    drive(motors_dict, vx=0, vy=-speed, omega=0)

def rotate_cw(motors_dict, speed=260):
    drive(motors_dict, vx=0, vy=0, omega=-speed)

def rotate_ccw(motors_dict, speed=260):
    drive(motors_dict, vx=0, vy=0, omega=speed)

def move_diagonal_front_right(motors_dict, speed=260):
    drive(motors_dict, vx=speed, vy=speed, omega=0)

def move_diagonal_front_left(motors_dict, speed=260):
    drive(motors_dict, vx=speed, vy=-speed, omega=0)

def move_diagonal_rear_right(motors_dict, speed=260):
    drive(motors_dict, vx=-speed, vy=speed, omega=0)

def move_diagonal_rear_left(motors_dict, speed=260):
    drive(motors_dict, vx=-speed, vy=-speed, omega=0)

def arc_turn_right(motors_dict, speed=260, turn_ratio=0.5):
    drive(motors_dict, vx=speed, vy=0, omega=-speed * turn_ratio)

def arc_turn_left(motors_dict, speed=260, turn_ratio=0.5):
    drive(motors_dict, vx=speed, vy=0, omega=speed * turn_ratio)

def move_for_seconds(fn, motors_dict, duration, **kwargs):
    fn(motors_dict, **kwargs)
    time.sleep(duration)
    stop_motors(motors_dict)


# ── Line follower ─────────────────────────────────────────────────────────────

def run_follow_line(motors_dict, trail_sensors_dict):
    BASE_SPEED       = 300
    TURN_DELTA_RIGHT = 110
    TURN_DELTA_LEFT  = 130
    RECOVER_SPEED    = 200

    print("Starting line follow")
    state.command_event.clear()
    last_direction = 0

    while not state.command_event.is_set():
        i7 = trail_sensors_dict['left'].get_state()
        i8 = trail_sensors_dict['right'].get_state()

        if i7 == 0 and i8 == 0:
            left, right = BASE_SPEED, BASE_SPEED
            motors_run(motors_dict, left, right)

        elif i7 == 0 and i8 == 1:
            left, right = BASE_SPEED - TURN_DELTA_LEFT, BASE_SPEED + TURN_DELTA_LEFT
            motors_run(motors_dict, left, right)
            last_direction = 1

        elif i7 == 1 and i8 == 0:
            left, right = BASE_SPEED + TURN_DELTA_RIGHT, BASE_SPEED - TURN_DELTA_RIGHT
            motors_run(motors_dict, left, right)
            last_direction = -1

        else:
            if last_direction >= 0:
                left, right = -RECOVER_SPEED, RECOVER_SPEED
            else:
                left, right = RECOVER_SPEED, -RECOVER_SPEED
            motors_run(motors_dict, left, right)

        state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "follow_line",
            "sensors": {
                "sensor_left":  i7,
                "sensor_right": i8,
            },
            "command": {
                "left_pwm":  left,
                "right_pwm": right
            }
        }))

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Line follow stopped")


# ── Wall follower ─────────────────────────────────────────────────────────────

def run_follow_wall(motors_dict, dist_sensor_dict):
    BASE_SPEED    = 220
    TARGET_DIST   = 12.0
    FRONT_TRIGGER = 25.0
    WALL_CLOSE    = 20.0
    MIN_TURN_TIME = 0.3
    MAX_TURN_TIME = 3.0
    Kp            = 3.0
    hist = [TARGET_DIST] * 3
    print("Starting wall follow")
    state.command_event.clear()
    mode       = "FOLLOW"
    turn_start = 0.0
    while not state.command_event.is_set():
        d_front = dist_sensor_dict['front'].get_distance()
        d_right = dist_sensor_dict['right'].get_distance()
        hist.pop(0)
        hist.append(d_right)
        d_right_avg = sum(hist) / 3.0
        if mode == "FOLLOW":
            error      = TARGET_DIST - d_right_avg
            correction = int(Kp * error)
            left_spd  = max(50, min(400, BASE_SPEED + correction))
            right_spd = max(50, min(400, BASE_SPEED - correction))
            print("[FOLLOW] front={:.1f} right={:.1f} left_spd={} right_spd={}".format(
                d_front, d_right_avg, left_spd, right_spd))
            motors_run(motors_dict, left_spd, right_spd)
            if d_front < FRONT_TRIGGER:
                print("OBSTACLE -> TURNING")
                mode       = "TURN"
                turn_start = time.time()
                hist       = [TARGET_DIST] * 3
        else:  # TURN
            left_spd, right_spd = 80, 220
            motors_run(motors_dict, left_spd, right_spd)
            elapsed = time.time() - turn_start
            print("[TURN] front={:.1f} right={:.1f} t={:.2f}".format(
                d_front, d_right, elapsed))
            if elapsed >= MIN_TURN_TIME and d_front > FRONT_TRIGGER:
                print("WALL ACQUIRED -> FOLLOW")
                hist = [d_right] * 3
                mode = "FOLLOW"
            elif elapsed > MAX_TURN_TIME:
                print("TURN TIMEOUT -> FOLLOW")
                hist = [d_right] * 3
                mode = "FOLLOW"

        state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "follow_wall",
            "sensors": {
                "d_front": d_front,
                "d_right": d_right_avg,
            },
            "command": {
                "left_pwm":  left_spd,
                "right_pwm": right_spd
            }
        }))

        time.sleep(0.02)
    stop_motors(motors_dict)
    print("Wall follow stopped")

# ── Top-down obstacle avoidance ───────────────────────────────────────────────

STATE_FORWARD = "FORWARD"
STATE_TURN    = "TURN"
STATE_RECOVER = "RECOVER"

def _read_avg(sensor, n=3):
    readings = []
    for _ in range(n):
        readings.append(sensor.get_distance())
    return sum(readings) / n

def run_avoid_topdown(motors_dict, dist_sensor_dict):
    BASE_SPEED    = 220
    TURN_SPEED    = 180
    RECOVER_TIME  = 0.4
    FRONT_DIST    = 45.0
    SIDE_DIST     = 12.0

    print("Starting top-down obstacle avoidance")
    state.command_event.clear()

    current_state  = STATE_FORWARD
    recover_timer  = 0.0
    turn_direction = 0

    while not state.command_event.is_set():
        d_front = _read_avg(dist_sensor_dict['front'])
        d_left  = _read_avg(dist_sensor_dict['left'])
        d_right = _read_avg(dist_sensor_dict['right'])

        print("front={:.1f}  left={:.1f}  right={:.1f}  state={}".format(
            d_front, d_left, d_right, current_state))

        # --- Transitions ---
        if current_state == STATE_FORWARD:
            if d_front < FRONT_DIST:
                if d_right < d_left:
                    turn_direction = -1
                else:
                    turn_direction = 1
                current_state = STATE_TURN
                print("State -> TURN  direction={}  (front={:.1f}cm)".format(
                    turn_direction, d_front))

        elif current_state == STATE_TURN:
            if d_front >= FRONT_DIST:
                current_state = STATE_RECOVER
                recover_timer = time.time()
                print("State -> RECOVER")

        elif current_state == STATE_RECOVER:
            if time.time() - recover_timer > RECOVER_TIME:
                current_state  = STATE_FORWARD
                turn_direction = 0
                print("State -> FORWARD")

        # --- Actions ---
        if current_state == STATE_FORWARD:
            if d_right < SIDE_DIST:
                left, right = BASE_SPEED - 50, BASE_SPEED + 50
                motors_run(motors_dict, left, right)
            elif d_left < SIDE_DIST:
                left, right = BASE_SPEED + 50, BASE_SPEED - 50
                motors_run(motors_dict, left, right)
            else:
                left, right = BASE_SPEED, BASE_SPEED
                motors_run(motors_dict, left, right)

        elif current_state == STATE_TURN:
            if turn_direction == 1:
                left, right = BASE_SPEED + TURN_SPEED, BASE_SPEED - TURN_SPEED
                motors_run(motors_dict, left, right)
            else:
                left, right = BASE_SPEED - TURN_SPEED, BASE_SPEED + TURN_SPEED
                motors_run(motors_dict, left, right)

        elif current_state == STATE_RECOVER:
            left, right = BASE_SPEED, BASE_SPEED
            motors_run(motors_dict, left, right)

        state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "avoid_topdown",
            "sensors": {
                "d_front": d_front,
                "d_left":  d_left,
                "d_right": d_right,
            },
            "command": {
                "left_pwm":  left,
                "right_pwm": right
            }
        }))

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Top-down avoidance stopped")


# ── Braitenberg ───────────────────────────────────────────────────────────────

def _activation(distance_cm, max_dist=40.0, max_boost=200):
    distance_cm = max(0.1, min(distance_cm, max_dist))
    return int(max_boost * (1.0 - distance_cm / max_dist))

def run_braitenberg(motors_dict, dist_sensor_dict):
    BASE_SPEED = 220
    MAX_DIST   = 40.0

    print("Starting Braitenberg vehicle")
    state.command_event.clear()

    while not state.command_event.is_set():
        d_front = dist_sensor_dict['front'].get_distance()
        d_left  = dist_sensor_dict['left'].get_distance()
        d_right = dist_sensor_dict['right'].get_distance()

        # --- Activation par capteur ---
        act_front = _activation(d_front, MAX_DIST)
        act_left  = _activation(d_left,  MAX_DIST)
        act_right = _activation(d_right, MAX_DIST)

        # --- Connexions ipsilaterales ---
        left_speed  = BASE_SPEED + act_right - act_front
        right_speed = BASE_SPEED + act_left  - act_front

        left_speed  = max(-512, min(512, left_speed))
        right_speed = max(-512, min(512, right_speed))

        motors_run(motors_dict, left_speed, right_speed)

        state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "braitenberg",
            "sensors": {
                "d_front": d_front,
                "d_left":  d_left,
                "d_right": d_right,
            },
            "command": {
                "left_pwm":  left_speed,
                "right_pwm": right_speed
            }
        }))

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Braitenberg stopped")