
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import sys
import os
OUTPUT_PATH = Path(__file__).parent

from UI.main_menu.build.gui import start_app
start_app()