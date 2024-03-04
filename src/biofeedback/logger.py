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
import pyzmq
import json
from typing import NamedTuple


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
