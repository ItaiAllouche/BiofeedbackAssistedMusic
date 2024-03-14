import zmq #pip install pyzmq
import json
import sys
from typing import NamedTuple
import numpy as np
from biofeedback.settings import WATCH_SERVER_IP, WATCH_SERVER_PORT, HR_PROC_PORT, BVP_WINDOW_TIME
from biofeedback.estimation.bvp_to_hr.bvp2hr import get_hr_from_bvp


BVP_SAMPLING_RATE = 64
def run():
    context = zmq.Context()

    # Subscriber socket setup
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt(zmq.SUBSCRIBE, b'ibi')
    sub_socket.connect(f"tcp://{WATCH_SERVER_IP}:{WATCH_SERVER_PORT}")

    # Response socket setup
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind(f"tcp://*:{HR_PROC_PORT}")  # Binding to all available interfaces
    poller = zmq.Poller()
    poller.register(sub_socket, zmq.POLLIN)

    # class IBI(NamedTuple):
    #     ibi: float
    current_ibi:float = 1.0
    while True:
        _ = rep_socket.recv_pyobj()
        socks = dict(poller.poll(timeout=10))
        new_msg = sub_socket in socks and socks[sub_socket] == zmq.POLLIN
        if new_msg:
            data = json.loads(sub_socket.recv().decode().split(' ')[1])
            data = {k:float(v) for k,v in data.items()}
            current_ibi = data['ibi']
        hr = 60/current_ibi
        rep_socket.send_pyobj(hr)
    

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()