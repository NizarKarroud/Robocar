from schemas.car import CarStatus , ConnectionResponse , ConnectionStatus
import state
from database.db import save_car_status

def handle_control_response(payload: dict):
    response = ConnectionResponse(**payload)

    if response.status == ConnectionStatus.ACCEPTED and state.pending_key:
        state.active_key = state.pending_key
        state.pending_key = None
        state.connection_accepted = True
        state.connection_event.set()  

    elif response.status == ConnectionStatus.DISCONNECTED:
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()

def handle_car_status(payload: dict):
    car_status = CarStatus(**payload)
    save_car_status(car_status)



TOPIC_HANDLERS = {
    "control/response": handle_control_response,
    "status": handle_car_status,
}