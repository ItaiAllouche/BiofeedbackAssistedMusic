
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import sys
import os
OUTPUT_PATH = Path(__file__).parent


#############################################################################
    
# Main menu

def on_Start_run_button_click(window):
    window.destroy()
    print("Start run")
    import run_menu.build.gui
    run_menu.build.gui.start_run_menu()
    
    
def on_Settings_button_click(window):
    window.destroy()
    print("Settings")
    import settings.build.gui 
    settings.build.gui.start_settings_menu()
    
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
    
def on_Back_from_settings_button_click(window):
    window.destroy()
    import main_menu.build.gui
    main_menu.build.gui.start_main_menu()
    
    
#############################################################################

# Run menu

def on_Back_from_run_button_click(window):
    window.destroy()
    import main_menu.build.gui 
    main_menu.build.gui.start_main_menu()