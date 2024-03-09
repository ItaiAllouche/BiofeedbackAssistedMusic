import zmq #pip install pyzmq
import json
from typing import NamedTuple
import numpy as np
from biofeedback.settings import WATCH_SERVER_IP, WATCH_SERVER_PORT, SF_PROC_PORT, BVP_WINDOW_TIME
from biofeedback.estimation.bvp_to_hr.bvp2hr import get_hr_from_bvp


BVP_SAMPLING_RATE = 64
def run():
    context = zmq.Context()

    # Subscriber socket setup
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt(zmq.SUBSCRIBE, b'bvp')
    sub_socket.connect(f"tcp://{WATCH_SERVER_IP}:{WATCH_SERVER_PORT}")

    # Response socket setup
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind(f"tcp://*:{SF_PROC_PORT}")  # Binding to all available interfaces

    class BVP(NamedTuple):
        x: float


    bvp_window = []
    num_of_acc_readings = 0

    while True:
        _ = rep_socket.recv_pyobj()
        
        for _ in range(BVP_SAMPLING_RATE*BVP_WINDOW_TIME):
            # !!!Remember the tcp buffer from the phone!!!
            data: dict = json.loads(sub_socket.recv().decode().split(' ')[1])
            data = {k:int(v) for k,v in data.items()}
            bvp_data = BVP(**data)
            bvp_window.append(bvp_data)
        bvp = np.array(bvp_window)
        result: float = get_hr_from_bvp(bvp)
        rep_socket.send_pyobj(result)
        bvp_window = []
    

if __name__ == '__main__':
    run()