from biofeedback.acc2sf_offline import get_cadence
from biofeedback.media_player import Player 
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
# from dotenv import load_dotenv
# load_dotenv(dotenv_path='../.env')

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



def run():
    logger.info('Started controller')
    # initiate audio player
    player = Player.from_file(path=PLAYLIST)

    # module initialization
    # delta = 10
    #warm_up_time = 100 # in sec
    # runner_age = 26
    # runner_max_HR = 220 - runner_age # TODO: find more accurate formula
    low_HR, high_HR = 95.95, 134.33
    def get_optimal_heart_rate():
        return np.mean([low_HR, high_HR]).round(decimals=2)
    
    # Start of Warming Up period
    # time.sleep(warm_up_time)
    # optimal_HR = HR_to_optimal_HR(low_HR, high_HR)
    # End of Warming Up period

    # averaging cadence and HR in spans of 15 sec
    cadence = get_cadence(join(EMPATICA_RECORD, 'ACC.csv'), running=True) # assuming cadence is measured after warm up period
    # print(f'{np.count_nonzero(cadence)=}')
    cadence = cadence[:len(cadence)-len(cadence)%INTERVAL]
    cadence = cadence.reshape(-1, INTERVAL)
    cadence = np.mean(cadence, axis=1)

    df = pd.read_csv(join(EMPATICA_RECORD, 'HR.csv'), skiprows=2, header=None, names=['hr']) #  the signal is in 1Hz
    heart_rate_signal = df['hr'].to_numpy()
    heart_rate_signal = heart_rate_signal[:len(heart_rate_signal)-len(heart_rate_signal)%INTERVAL]
    heart_rate_signal = heart_rate_signal.reshape(-1, INTERVAL)
    heart_rate_signal = np.mean(heart_rate_signal, axis=1)
    least_length = min(len(heart_rate_signal), len(cadence))
    heart_rate_signal = heart_rate_signal[:least_length].round(decimals=2)
    cadence = cadence[:least_length].round(decimals=2)
    logger.debug(f'Cadence signal length: {len(cadence)}')
    logger.debug(f'HR signal signal length: {len(heart_rate_signal)}')

    samples = [Sample(*s) for s in zip(heart_rate_signal, cadence)]
    stable_countdown = STABLE_COUNTDOWN
    for i, sample in enumerate(samples):
        reset_flag = True
        hr, cadence = sample
        optimal_hr = get_optimal_heart_rate()
        hr_divergence = 100*(hr-optimal_hr)/optimal_hr
        tempo = player.current_song.tempo
        cadence_divergence = 100*(cadence*60-tempo)/tempo # beats per minute
        if(hr_divergence > THRESHOLD_HR and stable_countdown > 0): # HR too high
            if(cadence_divergence > THRESHOLD_CADANCE): # Running too fast
                log_down(i, sample)
            else:
                stable_countdown -= 1
                reset_flag = False
                log_unchanged(i, sample)
                logger.debug(f'{i}: {stable_countdown=}')
        elif(hr < -THRESHOLD_HR): # HR too low
            if(cadence_divergence < -THRESHOLD_CADANCE): # Running too slow
                log_up(i, sample)
            else:
                log_unchanged(i, sample)
        else: # HR is optimal
            if(cadence_divergence > THRESHOLD_CADANCE): # Running too fast
                log_down(i, sample)
            elif(cadence_divergence < -THRESHOLD_CADANCE): # Running too slow
                log_up(i, sample)
            else:
                log_unchanged(i, sample)
                logger.debug(f'{i}: On track')
        if(reset_flag):
            stable_countdown = STABLE_COUNTDOWN
        # time.sleep(INTERVAL)


if __name__ == '__main__':
    run()