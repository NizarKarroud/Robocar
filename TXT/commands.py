import time
import state


def stop_motors(motors_dict):
    m = motors_dict
    m['M1'].set_speed(0, m['CW'])
    m['M2'].set_speed(0, m['CW'])
    m['M3'].set_speed(0, m['CW'])
    m['M4'].set_speed(0, m['CW'])
    m['M1'].start_sync(m['M2'], m['M3'], m['M4'])
   


def motors_run(motors_dict, left_speed, right_speed):
    M2_BOOST = 30
    m = motors_dict
    boosted_right = min(right_speed + M2_BOOST, 512)

    m['M1'].set_speed(abs(left_speed),    m['CW']  if left_speed    >= 0 else m['CCW'])
    m['M2'].set_speed(abs(boosted_right), m['CCW'] if boosted_right >= 0 else m['CW'])
    m['M3'].set_speed(abs(right_speed),   m['CCW'] if right_speed   >= 0 else m['CW'])
    m['M4'].set_speed(abs(right_speed),   m['CCW'] if right_speed   >= 0 else m['CW'])
    m['M1'].start_sync(m['M2'], m['M3'], m['M4'])


def run_follow_line(motors_dict, trail_sensors_dict):
    BASE_SPEED       = 260
    TURN_DELTA_RIGHT = 120
    TURN_DELTA_LEFT  = 160
    RECOVER_SPEED    = 180

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

        time.sleep(0.01)

    stop_motors(motors_dict)
    print("Line follow stopped")