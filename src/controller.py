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

PLAYLIST = getenv('PLAYLIST', 'recordings/playlists/playlist.txt')
"""
Path to playlist.txt file
"""

EMPATICA_RECORD = getenv('EMPATICA_RECORD', 'recordings/empatica/gym_12kmh/')
"""
Path to empatica csv recording directory
"""

# endregion


class Runner:
    def __init__(self, low_hr: int, high_hr: int, age: int):
        self.low_hr = low_hr
        self.high_hr = high_hr
        self.age = age
        self.optimal_hr = 0


def get_optimal_heart_rate(runner: Runner):
    
    return np.mean([low_HR, high_HR]).round(decimals=2)


def calc_Next_tempo(runner: Runner, current_hr: float, current_cadence: float):
    '''
    calculate the change in bpm in percentage  TODO- make sense
    '''
    if runner.optimal_hr == current_hr:
        if current_cadence == runner.current_song_tempo:
            return  0
        elif current_cadence > runner.current_song_tempo:
            return 5
        else:
            return -5
    return 0


class Sample(NamedTuple):
    hr: float
    cadence: float


class Controller:
    def __init__(self, server_ip: str, sub_port: str, runner: Runner, playback_speed_change_interval: int = 30):
        # Subscriber socket setup
        self.SERVER_IP = server_ip
        self.SUB_PORT = sub_port
        self.context = zmq.Context()
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'hr')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'cadence')
        self.sub_socket.connect(f"tcp://{self.SERVER_IP}:{self.SUB_PORT}")
        
        # player setup
        self.music_player = Player.from_file(path=PLAYLIST)
        self.current_song_idx = 0
        self.playback_speed_change_interval = playback_speed_change_interval
        
        # calculator setup
        self.runner = runner
        self.current_hr = 0
        self.current_cadence = 0
        self.num_of_cadece_readings = 0


    def warm_up(self):
        time.sleep(WARM_UP_TIME)
        while True:
            topic, message = self.sub_socket.recv_multipart()
            data = json.loads(message)
            if topic == b'hr':
                self.current_hr = data['hr']
                self.runner.optimal_hr = get_optimal_heart_rate(self.runner)
            
    def run(self):
        while True:
            topic, message = self.sub_socket.recv_multipart()
            data = json.loads(message)
            if topic == b'hr':
                self.hr = data['hr']
            elif topic == b'cadence':
                self.cadence = data['cadence']
                self.num_of_cadece_readings += 1
            else:
                raise ValueError(f'Unknown topic {topic}') #TODO - handle this error or delete
            
            if self.num_of_cadece_readings == self.playback_speed_change_interval:
                self.num_of_cadece_readings = 0
                calc_Next_tempo(runner, self.hr, self.cadence)





if __name__ == "__main__":
    SERVER_IP = '....'  # Replace with your server IP
    SUB_PORT = '...'    # Replace with your subscriber port
    runner = Runner(low_hr=95.95, high_hr=134.33, age=26)
    controller = Controller(SERVER_IP, SUB_PORT, runner, INTERVAL)
    controller.warm_up()
    controller.run()