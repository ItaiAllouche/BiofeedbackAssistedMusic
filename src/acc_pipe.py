import zmq #pip install pyzmq
import json
from typing import NamedTuple

SERVER_IP = '....'
SUB_PORT = '...'
PUB_PORT = '...'

context = zmq.Context()

# Subscriber socket setup
sub_socket = context.socket(zmq.SUB)
sub_socket.setsockopt(zmq.SUBSCRIBE, b'acc')
sub_socket.connect(f"tcp://{SERVER_IP}:{SUB_PORT}")

# Publisher socket setup
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUB_PORT}")  # Binding to all available interfaces

class ACC(NamedTuple):
    x: float
    y: float
    z: float

acc_window = []
num_of_acc_readings = 0

def get_cadence(acc_window):
    return sum(acc_window) / len(acc_window) #TODO: check if this is the correct calculation


while True:
    topic, message = sub_socket.recv_multipart()
    data = json.loads(message)
    acc_data = ACC(acc=data['acc'])
    acc_window.append(acc_data)
    num_of_acc_readings += 1
    if num_of_acc_readings == 2:
        result = get_cadence(acc_window)
        acc_window = []
        num_of_acc_readings = 0
        pub_socket.send_string(json.dumps(result))

