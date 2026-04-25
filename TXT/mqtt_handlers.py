

def handle_control_request(payload: dict):
    ...


def handle_car_status(payload: dict):
    ...


TOPIC_HANDLERS = {
    "control/request": handle_control_request,
    "status": handle_car_status,
}