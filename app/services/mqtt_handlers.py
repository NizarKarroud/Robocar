from app.schemas.car import  ConnectionResponse , ConnectionStatus , CameraResponse
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
    if response.status == CameraResponse.ACCEPTED :
        state.CAMERA_STATUS = CameraResponse.ACCEPTED 
        state.CAMERA_URL = f"https://{response.car_ip}{response.path}"
        state.camera_event.set()  

    elif response.status == CameraResponse.DISCONNECTED:
        state.CAMERA_STATUS = CameraResponse.DISCONNECTED 
        state.CAMERA_URL = None
        state.camera_event.set()  

    elif response.status == CameraResponse.REJECTED:
        state.CAMERA_STATUS = CameraResponse.REJECTED 
        state.CAMERA_URL = None
        state.camera_event.set()  


    
TOPIC_HANDLERS = {
    "control/response": handle_control_response,
    "control/camera/response" : handle_control_camera_response ,

}