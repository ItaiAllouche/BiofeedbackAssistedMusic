import numpy as np
# import time
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

INTERVAL = int(getenv('INTERVAL', 10))
"""
Sensor window time
* Units in seconds
* Must be devisible by `10` (???)
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

# module initialization
# delta = 10
#warm_up_time = 100 # in sec
# runner_age = 26
# runner_max_HR = 220 - runner_age # TODO: find more accurate formula
low_HR, high_HR = 95.95, 134.33
def get_optimal_heart_rate():
    return np.mean([low_HR, high_HR]).round(decimals=2)


class Sample(NamedTuple):
    hr: float
    cadence: float

def get_logging_conf_path() -> str:
    """
    get logging.conf from package config directory
    https://setuptools.pypa.io/en/stable/userguide/datafiles.html#accessing-data-files-at-runtime
    """
    return str(files('biofeedback.config').joinpath('logging.conf'))

logging.config.fileConfig(get_logging_conf_path())
logger = logging.getLogger('ctrl')

# fhandler = logging.StreamHandler(sys.stdout)
# formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# fhandler.setFormatter(formatter)
# logger.addHandler(fhandler)
# logger.setLevel(logging.DEBUG)


def log(i: int, sample: Sample, text: str):
    """
    Logging with severity level `INFO`
    """
    logger.info(f'{i}: {text}   {sample=}')

def log_error(text: str):
    """
    Logging with severity level `ERROR`
    """
    logger.error(text)

def log_up(i: int, sample: Sample):
    log(i=i, sample=sample, text='tempo up')

def log_down(i: int, sample: Sample):
    log(i=i, sample=sample, text='tempo down')

def log_unchanged(i: int, sample: Sample):
    log(i=i, sample=sample, text='tempo unchanged')



# This module adapts music tempo to HR by the following rules:
# current HR & cadnece above/below optimal  -> speed up/down tempo
# every stabilization_period, a decision for changing the tempo will be taken
# this modules ignores warm up period


class Controller:
    def __init__(self, server_ip: str, sub_port: str, playback_speed_change_interval: int = 30):
        self.SERVER_IP = server_ip
        self.SUB_PORT = sub_port
        self.context = zmq.Context()
        
        # Subscriber socket setup
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'hr')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'cadence')
        self.sub_socket.connect(f"tcp://{self.SERVER_IP}:{self.SUB_PORT}")
        
        self.music_player = Player.from_file(path=PLAYLIST)
        self.current_song_idx = 0
        self.playback_speed_change_interval = playback_speed_change_interval
        
        self.hr = 0
        self.optimal_hr = get_optimal_heart_rate()
        self.cadence = 0
        self.num_of_cadece_readings = 0


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
                #TODO - add cadence to song tempo, optimal HR and cadence.....


if __name__ == "__main__":
    SERVER_IP = '....'  # Replace with your server IP
    SUB_PORT = '...'   # Replace with your subscriber port
    controller = Controller(SERVER_IP, SUB_PORT, INTERVAL)
    controller.run()