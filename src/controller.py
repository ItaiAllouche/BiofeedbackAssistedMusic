'''
This module adapts music tempo to HR by the following rules:
current HR & cadnece above/below optimal  -> speed up/down tempo
every stabilization_period, a decision for changing the tempo will be taken
this modules ignores warm up period
'''

import numpy as np
import time
import pandas as pd
from os import getenv
from os.path import join
from typing import List, NamedTuple
import logging
import logging.config
from importlib.resources import files
import sys
from media_player import Player
from playsound import playsound 
import random
import copy
# from dotenv import load_dotenv
# load_dotenv(dotenv_path='../.env')

import zmq
import json
from typing import NamedTuple

import logger

# region Constants

THRESHOLD_HR = int(getenv('THRESHOLD_HR', 10)) # In percentages
"""
Threashold for HR divergance from oprimal HR
* Units in precentages
"""

THRESHOLD_CADANCE = int(getenv('THRESHOLD_CADANCE', 10))# In percentages
"""
Threashold for cadence divergance from song tempo
* Units in precentages
"""

INTERVAL = int(getenv('INTERVAL', 30))
"""
Sensor window time
* Units in seconds
* Must be devisible by `10` (???)
"""

WARM_UP_TIME = int(getenv('WARM_UP_TIME', 120))
""" 
Warm up stage length
* Units in seconds
"""

STABLE_COUNTDOWN = int(getenv('STABLE_COUNTDOWN', 3))
"""
Number of interval with time `INTERVAL` to allow for HR stabilization
"""

HR_PROC_PORT = int(getenv('HR_PROC_PORT', 1111))
"""
Port num of HR process
"""

SF_PROC_PORT = int(getenv('SF_PROC_PORT', 2222))
"""
Port num of SF process
"""

SERVER_IP = getenv('SERVER_IP', '127.0.0.1')
"""
Running server ip
"""

PLAYLIST = getenv('PLAYLIST', './playlist/playlist.txt')
"""
Path to playlist.txt file
"""

SF_TEST_INTERVAL = float(getenv('RUNNING_DURATION', './playlist/playlist.txt'))
"""
Time in minutes per step freq test
"""


# endregion


class Runner:
    def __init__(self, low_hr: int, high_hr: int, age: int):
        self.low_hr = low_hr
        self.high_hr = high_hr
        self.age = age
        self.optimal_hr = 0


def get_optimal_heart_rate(runner: Runner, current_hr: float):  # TODO- allign between int and float
    range = (runner.high_hr - runner.low_hr)
    coefficient = (0.75 * range) # TODO- make sense and calculate with max and stuff.....
    warm_up_result = (runner.low_hr - current_hr)
    return runner.high_hr + coefficient*(warm_up_result/range)

def calc_tempo_change(runner: Runner, current_hr: float, current_cadence: float):
    '''
    calculate the change in bpm in percentage  TODO- make sense
    '''
    if runner.optimal_hr == current_hr:
        if current_cadence == runner.current_song_tempo:
            return 0
        elif current_cadence > runner.current_song_tempo:
            return 5
        else:
            return -5
    return 0


class Sample(NamedTuple):
    hr: float
    cadence: float

class TestPoint(NamedTuple):
    avg_hr: float
    avg_sf: float
    
class Parabola(NamedTuple):
    a: float
    b: float
    c: float

class OptHrPoint(NamedTuple):
    x: float
    y: float


class Controller:
    def __init__(self, server_ip: str, sub_port: str, runner: Runner, stable_countdown: int = 30):
        # Subscriber socket setup
        self.SERVER_IP = server_ip
        self.context = zmq.Context()
        self.hr_socket = self.context.socket(zmq.REQ)
        self.hr_socket.connect(f"tcp://{self.SERVER_IP}:{HR_PROC_PORT}")
        self.sf_socket = self.context.socket(zmq.REQ)
        self.sf_socket.connect(f"tcp://{self.SERVER_IP}:{SF_PROC_PORT}")
        self.sf_to_song_path: dict[int, str]
                
    def avg_hr_sf_over_interval(self, time_interval=SF_TEST_INTERVAL) -> TestPoint:
        hr_sum:float = 0
        hr_count:int = 0
        sf_sum:float = 0
        sf_count:int = 0
        finished_time = time.time() + SF_TEST_INTERVAL * 60
        while(time.time() < finished_time):
            hr_msg = self.hr_socket.recv_pyobj()
            hr_sum += hr_msg
            hr_count += 1
            sf_msg = self.sf_socket.recv_pyobj()
            sf_sum += sf_msg
            sf_count += 1
            
        return TestPoint(hr_sum/hr_count, sf_sum/sf_count)

    def clc_hr_over_sf_interval(self, wanted_sf: int) -> TestPoint:
        song_to_be_played_path = self.sf_to_song_path[wanted_sf]
        playsound(song_to_be_played_path)
        return self.avg_hr_sf_over_interval()
    
    def run_epoch(self, wanted_sf: list[int]) -> list[TestPoint]:
        '''
        calculate avg_hr and avg_sf from each sf in wanted_sf
        '''
        return [self.clc_hr_over_sf_interval(wanted_sf=sf) for sf in wanted_sf]
        
    def run(self, wanted_sf: list[int], n_epoch: int) -> dict[int, list[TestPoint]]:
        test_points: dict[int, list[TestPoint]] = {k:[] for k in wanted_sf}
        wanted_sf = copy.deepcopy(wanted_sf)
        for _ in range(n_epoch):
            pairs = zip(wanted_sf, self.run_epoch(wanted_sf))
            for sf,tp in pairs:
                test_points[sf].append(tp)
            random.shuffle(wanted_sf) # change step frequencies order on each epoch
        return test_points
        
    def est_polynom(self, wanted_sf: list[int], n_epoch: int) -> Parabola:
        points_dict = self.run(wanted_sf, n_epoch)
        pts = [tp for list_of_tp in points_dict.values() for tp in list_of_tp]
        x_pts = [p.avg_sf for p in pts]
        y_pts = [p.avg_hr for p in pts]
        coeffs = np.polyfit(x=x_pts, y=y_pts, deg=2)
        assert len(coeffs) == 3
        return Parabola(*coeffs)
                                        
    def clc_min(self, wanted_sf: list[int], n_epoch: int) -> OptHrPoint:
        parab = self.est_polynom(wanted_sf=wanted_sf, n_epoch=n_epoch)
        min_x = parab.c-(parab.b**2)/(4*parab.a)
        min_y = parab.a*min_x**2+parab.b*min_x+parab.c
        min_pt = OptHrPoint(x=min_x, y=min_y)
        return min_pt
        
        
        
        
        
        



if __name__ == "__main__":
    SERVER_IP = '....'  # Replace with your server IP
    SUB_PORT = '...'    # Replace with your subscriber port
    runner = Runner(low_hr=95.95, high_hr=134.33, age=26)
    controller = Controller(SERVER_IP, SUB_PORT, runner, STABLE_COUNTDOWN)
    controller.warm_up()
    controller.music_player.play()
    controller.run()