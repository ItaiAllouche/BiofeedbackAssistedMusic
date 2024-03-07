import zmq #pip install pyzmq
import json
from typing import NamedTuple
import numpy as np
from biofeedback.settings import WATCH_SERVER_IP, WATCH_SERVER_PORT, SF_PROC_PORT
from biofeedback.acc_to_sf.acc2sf import get_cadence


ACC_SAMPLING_RATE = 32
WINDOW_TIME = 10
def run():
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

    while True:
        _ = rep_socket.recv_pyobj()
        
        for _ in range(ACC_SAMPLING_RATE*WINDOW_TIME):
            # !!!Remember the tcp buffer from the phone!!!
            data: dict = json.loads(sub_socket.recv().decode().split(' ')[1])
            data = {k:int(v) for k,v in data.items()}
            acc_data = ACC(**data)
            acc_window.append(acc_data)
        acc_matrix = np.array(acc_window)
        result: float = get_cadence(acc_matrix)
        # result: float = 83
        rep_socket.send_pyobj(result)
        acc_window = []
        # num_of_acc_readings += 1
        # if num_of_acc_readings == 2:
        #     acc_window = []
        #     num_of_acc_readings = 0
        #     rep_socket.send_string(json.dumps(result))
    

if __name__ == '__main__':
    run()