'''
This module adapts music tempo to HR by the following rules:
current HR & cadnece above/below optimal  -> speed up/down tempo
every stabilization_period, a decision for changing the tempo will be taken
this modules ignores warm up period
'''
from biofeedback.settings import *
from biofeedback.structs import *
import numpy as np
import sys
import time
# from playsound import playsound 
import random
import copy
import zmq
from csv_logger import CsvLogger
from typing import NamedTuple

csvlogger = CsvLogger(filename=LOG_CSV,
                      fmt=f'%(message)s',
                      header=['sf', 'hr', 'tempo'])

class LogRow(NamedTuple):
    sf: float
    hr: float
    tempo: int


class Controller:
    def __init__(self, server_ip: str, sf_to_song_path: dict[int, str]):
        self.SERVER_IP = server_ip
        self.context = zmq.Context()
        self.sf_to_song_path = sf_to_song_path
        self.hr_socket = self.context.socket(zmq.REQ)
        self.hr_socket.connect(f"tcp://{self.SERVER_IP}:{HR_PROC_PORT}")
        self.sf_socket = self.context.socket(zmq.REQ)
        self.sf_socket.connect(f"tcp://{self.SERVER_IP}:{SF_PROC_PORT}")
                
    def avg_hr_sf_over_interval(self, current_tempo: float, time_interval=SF_TEST_INTERVAL) -> TestPoint:
        hr_sum:float = 0
        hr_count:int = 0
        sf_sum:float = 0
        sf_count:int = 0
        interval_in_sec = SF_TEST_INTERVAL * 60
        start_time = time.time()
        warmup_time = start_time + interval_in_sec//3
        end_time = start_time + interval_in_sec
        is_first = True
        while(time.time() < end_time):
            if(time.time() > warmup_time): # Calculating over only after half of the interval has passed
                # Resetting hr_history on first iteration
                self.hr_socket.send_pyobj(obj=is_first)
                if(is_first):
                    print(f'Finished warmup')
                    is_first = False
                self.sf_socket.send_pyobj(obj=['test'])
                hr_msg: float = self.hr_socket.recv_pyobj() # bvp estimation
                sf_msg: np.ndarray = self.sf_socket.recv_pyobj()
                hr_sum += hr_msg # bvp estimation
                hr_count += 1 # bvp estimation
                sf_sum += np.sum(sf_msg)
                sf_count += len(sf_msg)
                csvlogger.info(list(LogRow(sf=sf_msg.mean(), hr=hr_msg, tempo=current_tempo))) # bvp estimation
            
        return TestPoint(hr_sum/hr_count, sf_sum/sf_count)

    def clc_hr_over_sf_interval(self, wanted_sf: int) -> TestPoint:
        song_to_be_played_path = self.sf_to_song_path[wanted_sf]
        # playsound(song_to_be_played_path)
        print(f'Playing {song_to_be_played_path}')
        return self.avg_hr_sf_over_interval(current_tempo=wanted_sf*2)
    
    def run_epoch(self, wanted_sf: list[int]) -> list[TestPoint]:
        '''
        calculate avg_hr and avg_sf from each sf in wanted_sf
        '''
        return [self.clc_hr_over_sf_interval(wanted_sf=sf) for sf in wanted_sf]
        
    def run_all_epochs(self, wanted_sf: list[int], n_epoch: int) -> dict[int, list[TestPoint]]:
        '''Play list of epochs'''
        test_points: dict[int, list[TestPoint]] = {k:[] for k in wanted_sf}
        wanted_sf = copy.deepcopy(wanted_sf)
        for _ in range(n_epoch):
            pairs = zip(wanted_sf, self.run_epoch(wanted_sf))
            for sf,tp in pairs:
                test_points[sf].append(tp)
            random.shuffle(wanted_sf) # change step frequencies order on each epoch
        return test_points
        
    def est_polynom(self, wanted_sf: list[int], n_epoch: int) -> Parabola:
        points_dict = self.run_all_epochs(wanted_sf, n_epoch)
        pts = [tp for list_of_tp in points_dict.values() for tp in list_of_tp]
        x_pts = [p.avg_sf for p in pts]
        y_pts = [p.avg_hr for p in pts]
        coeffs = np.polyfit(x=x_pts, y=y_pts, deg=2)
        assert len(coeffs) == 3
        return Parabola(*coeffs)
                                        
    def clc_min_hr_pt(self, wanted_sf: list[int], n_epoch: int) -> OptHrPoint:
        parab = self.est_polynom(wanted_sf=wanted_sf, n_epoch=n_epoch)
        min_x = parab.c-(parab.b**2)/(4*parab.a)
        min_y = parab.a*min_x**2+parab.b*min_x+parab.c
        min_pt = OptHrPoint(x=min_x, y=min_y)
        return min_pt


def run():
    wanted_sf=[75,85]
    songs = [str(i) for i in wanted_sf]
    controller = Controller(SERVER_IP, {w_sf:song for w_sf, song in zip(wanted_sf, songs)})
    result = controller.clc_min_hr_pt(wanted_sf=wanted_sf, n_epoch=1)
    # result = controller.clc_min_hr_pt(wanted_sf=wanted_sf, n_epoch=1)
    print(result)
    

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()