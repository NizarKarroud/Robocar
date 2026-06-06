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
    TURN_DELTA   = 80
    MARGIN_CLOSE = 2.0
    MARGIN_FAR   = 2.0
    FRONT_DIST   = 40.0
    print("Starting wall follow")
    state.command_event.clear()
    while not state.command_event.is_set():
        dist       = dist_sensor_side.get_distance()
        dist_front = dist_sensor_front.get_distance()
        # --- obstacle devant -> tourne sans stopper ---
        if dist_front < FRONT_DIST:
            while not state.command_event.is_set():
                dist_front = dist_sensor_front.get_distance()
                motors_run(motors_dict,
                           BASE_SPEED - TURN_DELTA,
                           BASE_SPEED + TURN_DELTA)
                if dist_front >= FRONT_DIST:
                    break
                time.sleep(0.015)
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


# --- 4.3 Top-down : machine a etats -------------------------------------------
#
# Etats :
# FORWARD  : avance tout droit
# TURN     : obstacle devant, tourne a gauche
# RECOVER  : reprend la direction apres evitement

STATE_FORWARD = "FORWARD"
STATE_TURN    = "TURN"
STATE_RECOVER = "RECOVER"

def _read_avg(sensor, n=3):
    """Moyenne de n lectures pour filtrer le bruit."""
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
    print("Demarrage dans 5 secondes")
    time.sleep(5)

    current_state  = STATE_FORWARD
    recover_timer  = 0.0
    turn_direction = 0

    while True:
        d_front = _read_avg(dist_sensor_dict['front'])
        d_left  = _read_avg(dist_sensor_dict['left'])
        d_right = _read_avg(dist_sensor_dict['right'])

        print("front={:.1f}  left={:.1f}  right={:.1f}  state={}".format(
            d_front, d_left, d_right, current_state))

        # --- Transitions ---
        if current_state == STATE_FORWARD:
            if d_front < FRONT_DIST:
                if d_right < d_left:
                    turn_direction = -1   # obstacle a droite -> tourne gauche
                else:
                    turn_direction = 1    # obstacle a gauche -> tourne droite
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
                motors_run(motors_dict, BASE_SPEED - 50, BASE_SPEED + 50)
            elif d_left < SIDE_DIST:
                motors_run(motors_dict, BASE_SPEED + 50, BASE_SPEED - 50)
            else:
                motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

        elif current_state == STATE_TURN:
            if turn_direction == 1:
                motors_run(motors_dict,
                           BASE_SPEED + TURN_SPEED,
                           BASE_SPEED - TURN_SPEED)
            else:
                motors_run(motors_dict,
                           BASE_SPEED - TURN_SPEED,
                           BASE_SPEED + TURN_SPEED)

        elif current_state == STATE_RECOVER:
            motors_run(motors_dict, BASE_SPEED, BASE_SPEED)

        time.sleep(0.015)

# --- 4.4 Bottom-up : vehicule de Braitenberg ----------------------------------
#
# Vehicule 2b - Fear :
# capteur droit  -> moteur gauche  (fuit a gauche si obstacle a droite)
# capteur gauche -> moteur droit   (fuit a droite si obstacle a gauche)
# capteur avant  -> les deux moteurs ralentissent

def _activation(distance_cm, max_dist=40.0, max_boost=200):
    """
    Proche  -> activation forte
    Loin    -> activation faible
    """
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
        time.sleep(0.015)

    stop_motors(motors_dict)
    print("Braitenberg stopped")