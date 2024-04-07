import zmq #pip install pyzmq
import json
import sys
import numpy as np
import pandas as pd
import pickle
from typing import NamedTuple
from biofeedback.settings import WATCH_SERVER_IP, WATCH_SERVER_PORT, HR_PROC_PORT, BVP_WINDOW_TIME
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
    rep_socket.bind(f"tcp://*:{HR_PROC_PORT}")  # Binding to all available interfaces
    poller = zmq.Poller()
    poller.register(sub_socket, zmq.POLLIN)
    class BVP(NamedTuple):
        bvp: float

    bvp_window = []
    all_bvp = np.array([])
    while True:
        _ = rep_socket.recv_pyobj()
        for _ in range(BVP_SAMPLING_RATE*BVP_WINDOW_TIME):
            # !!!Remember the tcp buffer from the phone!!!
            data: dict = json.loads(sub_socket.recv().decode().split(' ')[1])
            data = {k:float(v) for k,v in data.items()}
            bvp_data = BVP(**data)
            bvp_window.append(bvp_data)
        bvp_vector = np.array(bvp_window)
        result: float = get_hr_from_bvp(bvp_vector.squeeze())
        rep_socket.send_pyobj(result)
        all_bvp = np.append(all_bvp, bvp_window)
        with open('/home/adam/Desktop/BiofeedbackAssistedMusic/logs/bvp.pkl', 'wb') as f: 
            pickle.dump(all_bvp, f) 
        # pd.DataFrame({'bvp':all_bvp}).to_csv('/home/adam/Desktop/BiofeedbackAssistedMusic/logs/bvp.csv')
        bvp_window = []

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()