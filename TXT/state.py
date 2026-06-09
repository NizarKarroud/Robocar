
import queue  , threading

CLIENT_ID = None
current_command = None     
command_event = threading.Event()  
command_queue = queue.Queue()
mqtt_client = None
motors_dict = None
last_sensors = {"left": None, "right": None, "front": None}
