
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import sys
import os
OUTPUT_PATH = Path(__file__).parent

import main_menu 
import settings 
import run_menu 
from run_menu.build.gui import *
from settings.build.gui import *
from main_menu.build.gui import *

#############################################################################
    
# Main menu

def on_Start_run_button_click():
    print("Start run")
    start_run_menu()
    
def on_Settings_button_click():
    print("Settings")
    start_settings_menu()
    
def on_Exit_button_click():
    print("Exit")
    sys.exit()
    
def on_Electronic_button_click():
    print("Electronic selected")
    # choose electronic music
    
def on_Rock_button_click():
    print("Rock selected")
    # choose rock music
    
def on_Metronome_button_click():
    print("Metronome selected")
    # choose metronome
    

#############################################################################

# Setting menu

def on_Set_button_click(warm_up_time, interval_time, threshold_hr):
    if warm_up_time <= 0 or interval_time <= 0 or threshold_hr <= 0:
        print("Invalid input")
        return
    
    # add more checks for valid input
    os.environ["WARM_UP_TIME"] = warm_up_time
    os.environ["INTERVAL_TIME"] = interval_time
    os.environ["THRESHOLD_HR"] = threshold_hr
    
def on_Back_from_settings_button_click(): 
    start_main_menu()
    
    
#############################################################################

# Run menu

def on_Back_from_run_button_click():
    start_main_menu()