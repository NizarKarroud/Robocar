from app.schemas.car import  ConnectionResponse , ConnectionStatus , CameraResponse , CameraRequestStatus
from app import state

def handle_control_response(payload: dict):
    response = ConnectionResponse(**payload.get("data"))
    if response.status == ConnectionStatus.ACCEPTED and state.pending_key:
        state.CAR_ID = response.car_id
        print(state.CAR_ID)
        state.active_key = state.pending_key
        state.pending_key = None
        state.connection_accepted = True
        state.connection_event.set()  

    elif response.status == ConnectionStatus.DISCONNECTED:
        state.CAR_ID = None
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()
    elif response.status == ConnectionStatus.REJECTED:
        state.CAR_ID = None
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()

def handle_control_camera_response(payload : dict):
    response = CameraResponse(**payload.get("data"))
    print(response)

    if response.status == CameraRequestStatus.ACCEPTED :
        state.CAMERA_STATUS = "accepted" 
        state.CAMERA_URL = f"https://{response.car_ip}:{response.port}{response.path}"
        state.camera_event.set()  

    elif response.status == CameraRequestStatus.DISCONNECTED:
        state.CAMERA_STATUS = "disconnected"
        state.CAMERA_URL = None
        state.camera_event.set()  

    elif response.status == CameraRequestStatus.REJECTED:
        state.CAMERA_STATUS = "rejected"
        state.CAMERA_URL = None
        state.camera_event.set()  


    
TOPIC_HANDLERS = {
    "control/response": handle_control_response,
    "control/camera/response" : handle_control_camera_response ,

}