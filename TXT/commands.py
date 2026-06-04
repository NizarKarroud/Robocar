import time
import state

# ── Robot physical parameters ────────────────────────────────────────────────
R  = 2.75   # Wheel radius (cm)
L  = 18.0   # Front-to-rear axle distance (cm)
W  = 22.6   # Left-to-right wheel distance (cm)
LX = L / 2  # 9.0  cm
LY = W / 2  # 11.3 cm

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
    k = LX + LY  # 20.3 cm
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


# ── Named movement functions ──────────────────────────────────────────────────

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


# ── Timed helper ──────────────────────────────────────────────────────────────

def move_for_seconds(fn, motors_dict, duration, **kwargs):
    fn(motors_dict, **kwargs)
    time.sleep(duration)
    stop_motors(motors_dict)


# ── Line follower (unchanged) ─────────────────────────────────────────────────
def run_follow_line(motors_dict, trail_sensors_dict):
    BASE_SPEED       = 300    # un peu moins vite = plus stable
    TURN_DELTA_RIGHT = 110    # correction plus douce
    TURN_DELTA_LEFT  = 130    # correction plus douce
    RECOVER_SPEED    = 200    # recovery plus douce

    print("Starting line follow")
    state.command_event.clear()

    last_direction = 0

    while not state.command_event.is_set():
        i7 = trail_sensors_dict['left'].get_state()
        i8 = trail_sensors_dict['right'].get_state()

        if i7 == 0 and i8 == 0:
            motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

        elif i7 == 0 and i8 == 1:
            motors_run(motors_dict, BASE_SPEED - TURN_DELTA_LEFT, BASE_SPEED + TURN_DELTA_LEFT)
            last_direction = 1

        elif i7 == 1 and i8 == 0:
            motors_run(motors_dict, BASE_SPEED + TURN_DELTA_RIGHT, BASE_SPEED - TURN_DELTA_RIGHT)
            last_direction = -1

        else:
            if last_direction >= 0:
                motors_run(motors_dict, -RECOVER_SPEED, RECOVER_SPEED)
            else:
                motors_run(motors_dict, RECOVER_SPEED, -RECOVER_SPEED)

        time.sleep(0.015)    # un peu plus de temps entre chaque lecture

    stop_motors(motors_dict)
    print("Line follow stopped")


def run_follow_wall(motors_dict, dist_sensor_side, dist_sensor_front, target_dist=15.0):
    BASE_SPEED   = 220
    TURN_DELTA   = 65     # un peu plus fort qu'avant
    MARGIN_CLOSE = 3.0
    MARGIN_FAR   = 3.0
    FRONT_DIST   = 40.0   # cm, seuil obstacle devant

    print("Starting wall follow")
    state.command_event.clear()

    while not state.command_event.is_set():
        dist       = dist_sensor_side.get_distance()
        dist_front = dist_sensor_front.get_distance()

        # --- obstacle devant -> tourne a gauche mais reste a droite ---
        if dist_front < FRONT_DIST:
            motors_run(motors_dict,
                       BASE_SPEED - TURN_DELTA,
                       BASE_SPEED + TURN_DELTA)

        # --- trop proche du mur ---
        elif dist < target_dist - MARGIN_CLOSE:
            motors_run(motors_dict,
                       BASE_SPEED - TURN_DELTA,
                       BASE_SPEED + TURN_DELTA)

        # --- trop loin du mur ---
        elif dist > target_dist + MARGIN_FAR:
            motors_run(motors_dict,
                       BASE_SPEED + TURN_DELTA,
                       BASE_SPEED - TURN_DELTA)

        # --- bonne distance ---
        else:
            motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Wall follow stopped")