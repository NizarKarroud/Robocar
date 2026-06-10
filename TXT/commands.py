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
    
    # state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
    #     "timestamp": datetime.now(timezone.utc).isoformat(),
    #     "mode": fn.__name__,
    #     "sensors": {},
    #     "command": {
    #         "duration": duration,
    #         "speed": kwargs.get("speed", 260)
    #     }
    # }))
    
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

        # state.mqtt_client.publish("car/{}/telemetry".format(state.CAR_ID), canonical_json({
        #     "timestamp": datetime.now(timezone.utc).isoformat(),
        #     "mode": "follow_line",
        #     "sensors": {
        #         "sensor_left":  i7,
        #         "sensor_right": i8,
        #     },
        #     "command": {
        #         "left_pwm":  left,
        #         "right_pwm": right
        #     }
        # }))

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Line follow stopped")


# ── Wall follower ─────────────────────────────────────────────────────────────

# ── Wall follower (right wall) ────────────────────────────────────────────────

def run_follow_wall(motors_dict, distance_sensors_dict):
    BASE_SPEED       = 300
    FRONT_DIST_STOP  = 24
    WALL_LOST        = 40
    WALL_LOST_FRAMES = 8
    WALL_TARGET      = 12
    Kp               = 8.0
    U_TURN_DURATION  = 1.4
    ROTATE_SPEED     = 340
    TURN_LEFT_MIN_MS = 400   # durée minimum de rotation avant de checker front
    FOLLOW_SETTLE_MS = 300   # délai après TURN_LEFT avant de pouvoir trigger U_TURN

    STATE_FOLLOW    = "FOLLOW"
    STATE_TURN_LEFT = "TURN_LEFT"
    STATE_U_TURN    = "U_TURN"

    current_state    = STATE_FOLLOW
    u_turn_start     = 0.0
    wall_lost_count  = 0
    turn_start_time  = 0.0
    follow_since     = time.time()   # quand on est entré en FOLLOW

    print("Starting right wall follow")
    state.command_event.clear()

    while not state.command_event.is_set():
        dist_front = min(distance_sensors_dict['front'].get_distance(), 60)
        dist_right = min(distance_sensors_dict['right'].get_distance(), 60)

        now = time.time()

        # ── Transitions ──────────────────────────────────────────────────────
        if current_state == STATE_FOLLOW:
            follow_elapsed_ms = (now - follow_since) * 1000

            if dist_front < FRONT_DIST_STOP:
                wall_lost_count = 0
                current_state   = STATE_TURN_LEFT
                turn_start_time = now
                print("→ TURN_LEFT")

            # U_TURN seulement si on est en FOLLOW depuis assez longtemps
            # (évite de trigger pendant le settle post-TURN_LEFT)
            elif follow_elapsed_ms > FOLLOW_SETTLE_MS and dist_right > WALL_LOST:
                wall_lost_count += 1
                if wall_lost_count >= WALL_LOST_FRAMES:
                    wall_lost_count = 0
                    current_state   = STATE_U_TURN
                    u_turn_start    = now
                    print("→ U_TURN")
            else:
                wall_lost_count = 0

        elif current_state == STATE_TURN_LEFT:
            turn_elapsed_ms = (now - turn_start_time) * 1000
            # attendre le minimum ET que le front soit libre
            if turn_elapsed_ms >= TURN_LEFT_MIN_MS and dist_front >= FRONT_DIST_STOP:
                current_state = STATE_FOLLOW
                follow_since  = now
                print("→ FOLLOW")

        elif current_state == STATE_U_TURN:
            elapsed = now - u_turn_start
            if elapsed >= U_TURN_DURATION and dist_right <= WALL_LOST:
                current_state = STATE_FOLLOW
                follow_since  = now
                print("→ FOLLOW (U-turn done)")
            elif dist_front < FRONT_DIST_STOP:
                current_state   = STATE_TURN_LEFT
                turn_start_time = now
                print("→ TURN_LEFT")

        # ── Actions ───────────────────────────────────────────────────────────
        if current_state == STATE_FOLLOW:
            error      = dist_right - WALL_TARGET
            correction = int(Kp * error)
            correction = max(-150, min(150, correction))
            left  = BASE_SPEED + correction
            right = BASE_SPEED - correction
            motors_run(motors_dict, left, right)
            print("FOLLOW right={:.1f}  err={:.1f}  corr={}".format(dist_right, error, correction))

        elif current_state == STATE_TURN_LEFT:
            rotate_cw(motors_dict, speed=ROTATE_SPEED)

        elif current_state == STATE_U_TURN:
            rotate_ccw(motors_dict, speed=ROTATE_SPEED)

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Right wall follow stopped")
 
# ── Top-down obstacle avoidance ───────────────────────────────────────────────

STATE_FORWARD = "FORWARD"
STATE_TURN    = "TURN"

def _read_avg(sensor, n=3):
    readings = []
    for _ in range(n):
        readings.append(sensor.get_distance())
    return sum(readings) / n

def run_avoid_topdown(motors_dict, dist_sensor_dict):
    BASE_SPEED    = 280
    TURN_SPEED    = 300
    FRONT_TRIGGER = 30.0   # distance à laquelle on commence à réagir
    SIDE_DIST     = 30.0   # distance à laquelle on corrige la dérive latérale
    SIDE_CORRECT  = 80     # correction latérale douce
    MIN_TURN_TIME = 0.5    # temps minimum de rotation avant de checker si la voie est libre

    print("Starting top-down obstacle avoidance")
    state.command_event.clear()

    current_state  = STATE_FORWARD
    turn_direction = 0
    turn_start     = 0.0

    while not state.command_event.is_set():
        d_front = _read_avg(dist_sensor_dict['front'])
        d_left  = _read_avg(dist_sensor_dict['left'])
        d_right = _read_avg(dist_sensor_dict['right'])

        print("front={:.1f}  left={:.1f}  right={:.1f}  state={}".format(
            d_front, d_left, d_right, current_state))

        # --- Transitions ---
        if current_state == STATE_FORWARD:
            if d_front < FRONT_TRIGGER:
                # choisit le côté le plus libre
                turn_direction = 1 if d_left > d_right else -1
                current_state  = STATE_TURN
                turn_start     = time.time()
                print("State -> TURN  direction={}".format(turn_direction))

        elif current_state == STATE_TURN:
            elapsed = time.time() - turn_start
            if elapsed >= MIN_TURN_TIME and d_front >= FRONT_TRIGGER:
                current_state  = STATE_FORWARD
                turn_direction = 0
                print("State -> FORWARD")

        # --- Actions ---
        if current_state == STATE_FORWARD:
            # correction latérale douce
            if d_right < SIDE_DIST:
                left, right = BASE_SPEED + SIDE_CORRECT, BASE_SPEED - SIDE_CORRECT
            elif d_left < SIDE_DIST:
                left, right = BASE_SPEED - SIDE_CORRECT, BASE_SPEED + SIDE_CORRECT
            else:
                left, right = BASE_SPEED, BASE_SPEED

        elif current_state == STATE_TURN:
            if turn_direction == 1:   # tourne gauche
                left, right = -TURN_SPEED, TURN_SPEED
            else:                     # tourne droite
                left, right = TURN_SPEED, -TURN_SPEED

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

def _activation(distance_cm, safe_dist):
    if distance_cm >= safe_dist:
        return 0.0
    ratio = 1.0 - (distance_cm / safe_dist)
    return ratio ** 2

# ── Braitenberg vehicle — 3 capteurs (front, right, left) ────────────────────

def run_braitenberg(motors_dict, dist_sensor_dict):
    BASE_SPEED  = 250
    MAX_SENSOR  = 60.0       # clamp capteurs — 1023 devient 60 → pf=0
    MIN_DIST    = 3.0
    MAX_PWM     = 480
    ESCAPE_DIST = 15.0       # front < 15cm → on compte les frames
    ESCAPE_FRAMES = 5        # 5 frames consécutives → escape
    ESCAPE_DURATION = 0.6    # secondes de recul

    W_FL = -400.0
    W_FR = -400.0
    W_RL =  300.0
    W_RR = -300.0
    W_LL = -300.0
    W_LR =  300.0

    def proximity(d):
        d = max(MIN_DIST, min(d, MAX_SENSOR))
        return 1.0 - (d / MAX_SENSOR)

    print("Starting Braitenberg vehicle 2b")
    state.command_event.clear()

    stuck_count  = 0
    escape_until = 0.0

    while not state.command_event.is_set():
        now = time.time()

        d_front = dist_sensor_dict['front'].get_distance()
        d_right = dist_sensor_dict['right'].get_distance()
        d_left  = dist_sensor_dict['left'].get_distance()

        # ── Escape mode ───────────────────────────────────────────────────────
        if now < escape_until:
            # choisit le côté le plus libre pour reculer en biais
            if d_right > d_left:
                move_backward(motors_dict, speed=280)   # recul droit
            else:
                move_backward(motors_dict, speed=280)
            print("[ESCAPE] f={:.1f} r={:.1f} l={:.1f}".format(d_front, d_right, d_left))
            time.sleep(0.02)
            continue

        # ── Détection coin / stuck ────────────────────────────────────────────
        if d_front < ESCAPE_DIST:
            stuck_count += 1
            if stuck_count >= ESCAPE_FRAMES:
                stuck_count  = 0
                escape_until = now + ESCAPE_DURATION
                print("[ESCAPE] triggered — front={:.1f}".format(d_front))
                continue
        else:
            stuck_count = 0

        # ── Braitenberg normal ────────────────────────────────────────────────
        pf = proximity(d_front)
        pr = proximity(d_right)
        pl = proximity(d_left)

        left_spd  = BASE_SPEED + W_FL * pf + W_RL * pr + W_LL * pl
        right_spd = BASE_SPEED + W_FR * pf + W_RR * pr + W_LR * pl

        left_spd  = int(max(-MAX_PWM, min(MAX_PWM, left_spd)))
        right_spd = int(max(-MAX_PWM, min(MAX_PWM, right_spd)))

        print("[BRAITENBERG] f={:.1f} r={:.1f} l={:.1f} | pf={:.2f} pr={:.2f} pl={:.2f} | L={} R={}".format(
            d_front, d_right, d_left, pf, pr, pl, left_spd, right_spd))

        motors_run(motors_dict, left_spd, right_spd)
        time.sleep(0.02)

    stop_motors(motors_dict)
    print("Braitenberg stopped")

def run_figure8_all(motors_dict, lam=15.0, omega_traj=0.30):
    mode_duration = 4.0 * math.pi / omega_traj   # 2 loops on the lemniscate
    dt = 0.015

    def pause_5s():
        for _ in range(500):
            if state.command_event.is_set():
                return True
            time.sleep(0.01)
        return False

    def run_mode(mode_name):
        print("Starting figure-8 mode={}".format(mode_name))
        t = 0.0

        while t < mode_duration:
            if state.command_event.is_set():
                return True

            dx = math.cos(t)
            dy = math.cos(2.0 * t)

            vx_i = lam * omega_traj * dx
            vy_i = lam * omega_traj * dy

            if mode_name == "theta_const":
                vx = vx_i
                vy = vy_i
                omega = 0.0

            elif mode_name == "standard":
                psi = math.atan2(dx, dy)
                vx = vx_i * math.cos(psi) + vy_i * math.sin(psi)
                vy = -vx_i * math.sin(psi) + vy_i * math.cos(psi)

                denom = 2.0 * (dx * dx + dy * dy)
                if denom > 1e-6:
                    omega = omega_traj * (2.0 * dx * math.sin(2.0 * t) + math.sin(t) * dy) / denom
                else:
                    omega = 0.0

            elif mode_name == "tomography":
                angle = omega_traj * t
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                vx = lam * omega_traj * (dx * cos_a + dy * sin_a)
                vy = lam * omega_traj * (-dx * sin_a + dy * cos_a)
                omega = omega_traj

            else:
                print("Unknown mode: {}".format(mode_name))
                return False

            drive(motors_dict, vx=vx, vy=vy, omega=omega)
            time.sleep(dt)
            t += omega_traj * dt

        stop_motors(motors_dict)
        print("Done with {}, waiting 5s...".format(mode_name))
        return pause_5s()

    state.command_event.clear()

    for mode_name in ["theta_const", "standard", "tomography"]:
        stopped = run_mode(mode_name)
        if stopped:
            break

    stop_motors(motors_dict)
    print("All modes done")