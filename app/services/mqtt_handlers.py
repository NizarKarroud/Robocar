from app.schemas.car import CarStatus , ConnectionResponse , ConnectionStatus
from app import state

def handle_control_response(payload: dict):
    response = ConnectionResponse(**payload.get("data"))
    print(response.model_dump_json())
    if response.status == ConnectionStatus.ACCEPTED and state.pending_key:
        state.active_key = state.pending_key
        state.pending_key = None
        state.connection_accepted = True
        state.connection_event.set()  

    elif response.status == ConnectionStatus.DISCONNECTED:
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()
    elif response.status == ConnectionStatus.REJECTED:
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()


TOPIC_HANDLERS = {
    "control/response": handle_control_response,
}