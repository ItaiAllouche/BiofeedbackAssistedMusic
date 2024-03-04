import zmq #pip install pyzmq
import json
from typing import NamedTuple
from biofeedback.settings import WATCH_SERVER_IP, WATCH_SERVER_PORT, SF_PROC_PORT
context = zmq.Context()

# Subscriber socket setup
sub_socket = context.socket(zmq.SUB)
sub_socket.setsockopt(zmq.SUBSCRIBE, b'acc')
sub_socket.connect(f"tcp://{WATCH_SERVER_IP}:{WATCH_SERVER_PORT}")

# Response socket setup
rep_socket = context.socket(zmq.REP)
rep_socket.bind(f"tcp://*:{SF_PROC_PORT}")  # Binding to all available interfaces

class ACC(NamedTuple):
    x: int
    y: int
    z: int


acc_window = []
num_of_acc_readings = 0

def get_cadence(acc_window):
    return sum(acc_window) / len(acc_window) #TODO: check if this is the correct calculation


while True:
    data: dict = json.loads(sub_socket.recv().decode().split(' ')[1])
    data = {k:int(v) for k,v in data.items()}
    acc_data = ACC(**data)
    acc_window.append(acc_data)
    num_of_acc_readings += 1
    if num_of_acc_readings == 2:
        result = get_cadence(acc_window)
        acc_window = []
        num_of_acc_readings = 0
        rep_socket.send_string(json.dumps(result))

