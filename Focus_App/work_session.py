# ../ to import path; and search ../ first
import os
os.chdir("../")

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from helper_scripts.helperFunctions import writeToPickle, loadPickle, loadPickle # had to change imports to use Qt4Agg

os.chdir("./Focus_App/")

from datetime import datetime

class WorkSession: 
    def __init__(self):
        self.timestamp = datetime.now()
        self.total_avg = 0

    def start(self):
        print("started work session :D ")
    def end(self): 
        print("ended work session")
