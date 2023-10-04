import zmq #pip install pyzmq
import json
from typing import NamedTuple

SERVER_IP = '....'
SUB_PORT = '...'
PUB_PORT = '...'

context = zmq.Context()

# Subscriber socket setup
sub_socket = context.socket(zmq.SUB)
sub_socket.setsockopt(zmq.SUBSCRIBE, b'ibi')
sub_socket.connect(f"tcp://{SERVER_IP}:{SUB_PORT}")

# Publisher socket setup
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUB_PORT}")  # Binding to all available interfaces

class IBI(NamedTuple):
    ibi: float



ibi_window = []
num_of_ibi_readings = 0

def calculate_ibi(ibi_window):
    return sum(ibi_window) / len(ibi_window) #TODO: check if this is the correct calculation


while True:
    topic, message = sub_socket.recv_multipart()
    data = json.loads(message)
    ibi_data = IBI(ibi=data['ibi'])
    ibi_window.append(ibi_data)
    num_of_ibi_readings += 1
    if num_of_ibi_readings == 2:
        result = calculate_ibi(ibi_window)
        ibi_window = []
        num_of_ibi_readings = 0
        pub_socket.send_string(json.dumps(result))
