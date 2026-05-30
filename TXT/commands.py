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
    """
    Low-level Mecanum drive.
    fl = front-left  (M1)
    fr = front-right (M2)  ← has hardware boost
    rl = rear-left   (M3)
    rr = rear-right  (M4)
    Positive = forward, negative = backward. Range: -512 to 512.
    """
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
    """Legacy 2-wheel-style drive, kept for line follower."""
    motors_mecanum(motors_dict, left_speed, right_speed, left_speed, right_speed)


# ── Kinematic model (eq. 1.20 from document) ─────────────────────────────────
# ω_wheels = H · u,   u = [vx, vy, ω]
#
#        1  [ 1   -1  -(LX+LY) ] [vx]
# ωi = ─── [ 1    1   (LX+LY) ] [vy]
#        R  [ 1    1  -(LX+LY) ] [ω ]
#           [ 1   -1   (LX+LY) ]
#
# Returns wheel speeds [w1_fr, w2_fl, w3_rl, w4_rr] in cm/s

def compute_wheel_speeds(vx, vy, omega):
    """
    Compute individual wheel speeds from desired robot velocity.
    vx    : forward velocity  (cm/s)
    vy    : lateral velocity  (cm/s, positive = right)
    omega : rotational speed  (rad/s, positive = CCW)
    Returns (fr, fl, rl, rr) in cm/s.
    """
    k = LX + LY  # 20.3 cm
    w1_fr = (1 / R) * ( vx - vy - k * omega)
    w2_fl = (1 / R) * ( vx + vy + k * omega)
    w3_rl = (1 / R) * ( vx - vy + k * omega)
    w4_rr = (1 / R) * ( vx + vy - k * omega)
    return w1_fr, w2_fl, w3_rl, w4_rr


def _scale_to_pwm(wheel_speeds, max_pwm=512):
    """Scale cm/s wheel speeds to PWM range [-512, 512]."""
    max_speed = max(abs(w) for w in wheel_speeds)
    if max_speed == 0:
        return (0, 0, 0, 0)
    scale = max_pwm / max_speed
    return tuple(int(w * scale) for w in wheel_speeds)


def drive(motors_dict, vx, vy, omega, max_pwm=512):
    """
    High-level kinematic drive.
    Computes wheel speeds from (vx, vy, omega) and sends to motors.
    vx    : forward  (+) / backward (-)
    vy    : strafe right (+) / left (-)
    omega : rotate CCW (+) / CW (-)
    max_pwm: scales output to this PWM ceiling (default 512)
    """
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
    """
    Run any movement function for `duration` seconds then stop.
    Usage: move_for_seconds(move_forward, motors_dict, 2.0, speed=300)
    """
    fn(motors_dict, **kwargs)
    time.sleep(duration)
    stop_motors(motors_dict)


# ── Line follower (unchanged) ─────────────────────────────────────────────────

# def run_follow_line(motors_dict, trail_sensors_dict):
#     BASE_SPEED       = 260
#     TURN_DELTA_RIGHT = 120
#     TURN_DELTA_LEFT  = 160
#     RECOVER_SPEED    = 180

#     print("Starting line follow")
#     state.command_event.clear()

#     last_direction = 0

#     while not state.command_event.is_set():
#         i7 = trail_sensors_dict['left'].get_state()
#         i8 = trail_sensors_dict['right'].get_state()

#         if i7 == 0 and i8 == 0:
#             motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

#         elif i7 == 0 and i8 == 1:
#             motors_run(motors_dict, BASE_SPEED - TURN_DELTA_LEFT, BASE_SPEED + TURN_DELTA_LEFT)
#             last_direction = 1

#         elif i7 == 1 and i8 == 0:
#             motors_run(motors_dict, BASE_SPEED + TURN_DELTA_RIGHT, BASE_SPEED - TURN_DELTA_RIGHT)
#             last_direction = -1

#         else:
#             if last_direction >= 0:
#                 motors_run(motors_dict, -RECOVER_SPEED, RECOVER_SPEED)
#             else:
#                 motors_run(motors_dict, RECOVER_SPEED, -RECOVER_SPEED)

#         time.sleep(0.01)

#     stop_motors(motors_dict)
#     print("Line follow stopped")


def run_follow_line(motors_dict, trail_sensors_dict):
    BASE_SPEED       = 220
    TURN_DELTA_RIGHT = 100
    TURN_DELTA_LEFT  = 100
    RECOVER_SPEED    = 150

    print("Starting line follow")
    state.command_event.clear()

    last_direction = 0

    while not state.command_event.is_set():
        i7 = trail_sensors_dict['left'].get_state()
        i8 = trail_sensors_dict['right'].get_state()

        # 0 = noir (sur la ligne), 1 = blanc (hors ligne)
        if i7 == 1 and i8 == 1:
            # centre sur la ligne
            motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

        elif i7 == 1 and i8 == 0:
            # droite hors ligne -> tourne droite
            motors_run(motors_dict, BASE_SPEED + TURN_DELTA_RIGHT, BASE_SPEED - TURN_DELTA_RIGHT)
            last_direction = 1

        elif i7 == 0 and i8 == 1:
            # gauche hors ligne -> tourne gauche
            motors_run(motors_dict, BASE_SPEED - TURN_DELTA_LEFT, BASE_SPEED + TURN_DELTA_LEFT)
            last_direction = -1

        else:
            # les deux hors ligne -> recuperation dans la derniere direction connue
            if last_direction > 0:
                motors_run(motors_dict, RECOVER_SPEED, -RECOVER_SPEED)
            elif last_direction < 0:
                motors_run(motors_dict, -RECOVER_SPEED, RECOVER_SPEED)
            else:
                motors_run(motors_dict, 0, 0)

        time.sleep(0.01)

    stop_motors(motors_dict)
    print("Line follow stopped")