from os import getenv
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

WATCH_SERVER_PORT = int(getenv('WATCH_SERVER_PORT', 5050))
"""
Port num of watch server, i.e phone
"""

ACC_WINDOW_TIME = int(getenv('ACC_WINDOW_TIME', 10))
"""
Cadance measuring window time (must be greater than `min_t`)
"""

BVP_WINDOW_TIME = int(getenv('BVP_WINDOW_TIME', 10))
"""
BVP measuring window time
"""

WATCH_SERVER_IP = getenv('WATCH_SERVER_IP', '192.168.3.200')
"""
IP of watch server, i.e phone
"""

SERVER_IP = getenv('SERVER_IP', '127.0.0.1')
"""
Running server ip
"""

PLAYLIST = getenv('PLAYLIST', './playlist/playlist.txt')
"""
Path to playlist.txt file
"""

SF_TEST_INTERVAL = float(getenv('SF_TEST_INTERVAL', 1.5))
"""
Time in minutes per step freq test
"""
LOG_CSV =  getenv('LOG_CSV', '/home/dogomen11/BiofeedbackAssistedMusic/logs/run.csv')
"""
Path to csv log directory
"""
