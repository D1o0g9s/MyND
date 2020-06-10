# ../ to import path; and search ../ first
import os
os.chdir("../")

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from helper_scripts.helperFunctions import writeToPickle, loadPickle, loadPickle # had to change imports to use Qt4Agg
from helper_scripts.helperFunctions import filterEEG
from helper_scripts.dataAnalysisFunctions import getIntervals 
from helper_scripts.PsychoPyConstants import SCALE_FACTOR_EEG

os.chdir("./Focus_App/")

from datetime import datetime
import time
import numpy as np
import torch
from pyOpenBCI import OpenBCICyton
import pyeeg
import threading
import random


DEFAULT_SECONDS = 5
DEFAULT_FS = 250
DEFAULT_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7]
DEFAULT_BINNING=[4, 8, 12, 20, 30]
DEFAULT_UPDATE_SECONDS = 0.5
LIVE_DATA = True

class WorkSession: 
    def __init__(self):
        # Import model
        self.fs = DEFAULT_FS
        self.buffer_seconds = DEFAULT_SECONDS
        self.started = False

    def start(self):
        print("started work session :D ")
        self.timestamp = datetime.now()
        self.model = torch.load("../data_analysis/models/model_t_combined_continuous_filtered_3class.pickle")
        self.focus_logger = FocusLogger(fs=self.fs)
        self.eeg_sampler = EEGSampler(fs=self.fs, buffer_seconds=self.buffer_seconds, update_seconds=DEFAULT_UPDATE_SECONDS, channels=DEFAULT_CHANNELS, binning=DEFAULT_BINNING, live=True, model=self.model, to_clean=True, three_class=True, focus_logger=self.focus_logger)
        if LIVE_DATA: 
            self.board = OpenBCICyton()
            self.eeg_thread = threading.Thread(target=self.board.start_stream, args=(self.eeg_sampler.push_data_sample,))
            self.eeg_thread.start()
        self.started = True

    def end(self): 
        print("ended work session")
        self.duration = datetime.utcfromtimestamp((datetime.now() - self.timestamp).total_seconds()).strftime('%H:%M:%S')

        if LIVE_DATA: 
            self.board.stop_stream()
        self.started = False
    
    def getTotalAvg(self):
        return self.focus_logger.getTotalAvg()

    def getTimestamp(self):
        return self.timestamp
    def getDuration(self):
        if self.started:
            self.duration = datetime.utcfromtimestamp((datetime.now() - self.timestamp).total_seconds()).strftime('%H:%M:%S')
        return self.duration
        
    def getEEGBufferData(self):
        return self.eeg_sampler.getBuffer()
    def getAveragedFocusBufferData(self):
        return self.eeg_sampler.getAveragedFocus()

class FocusLogger: 
    def __init__(self, fs):
        self.focus_values = [] 
        self.fs = fs
    def addFocusValue(self, val):
        self.focus_values.append(val)
    def getAvgOverPastSeconds(self, seconds):
        num_timepoints = max(len(self.focus_values, seconds * self.fs))
        vals = self.focus_values[-num_timepoints:]
        return np.mean(vals)
    def getTotalAvg(self):
        return np.mean(self.focus_values)
        
class EEGSampler:
    """ Holds a buffer of EEG data and accepts a single data sample as input to append to the buffer
    """
    def __init__(self, fs=DEFAULT_FS, buffer_seconds=DEFAULT_SECONDS, update_seconds=DEFAULT_UPDATE_SECONDS, channels=DEFAULT_CHANNELS, binning=DEFAULT_BINNING, live=True, model=None, to_clean=True, three_class=False, focus_logger=None):
        self.fs = fs
        self.buffer_seconds = buffer_seconds
        self.channels = channels # These are the channels we want
        
        self.live = live
        self.model = model
        
        self.buffer = np.zeros((fs * buffer_seconds, len(channels)))
        self.raw_buffer = np.zeros((fs * buffer_seconds, len(channels)))
        self.dc_removed_buffer = np.zeros((fs * buffer_seconds, len(channels)))
        
        self.binning = binning
        self.intervals = getIntervals(self.binning)
        self.power_bin_values = np.zeros((fs * buffer_seconds, len(self.intervals), len(self.channels)))
        self.focus = np.zeros((fs * buffer_seconds))
        self.focus_average = np.zeros((fs * buffer_seconds))
        self.update_seconds = update_seconds
        self.last_updated = time.time()
        self.mean = np.zeros(len(channels))
        self.count_samples = 0
        self.num_focused = 0 
        self.to_clean = to_clean
        self.three_class = three_class
        self.focus_logger = focus_logger
        
    def __filter_eeg(self):
        # Bandpass + 60 Hz Notch
        for i, chan in enumerate(self.channels):
            self.buffer[:self.count_samples, i] = filterEEG(self.dc_removed_buffer[:self.count_samples, i], self.fs, (0.5, 50))

    def __update_focus(self):
        data = np.transpose(self.buffer[:500])
        if self.three_class : 
            self.focus[0] = self.model.predict_classes(np.array([data]))[0] - 1
        else :
            self.focus[0] = 1 if self.model.predict_classes(np.array([data]))[0] > 0 else -1
        self.focus_average[0] = np.mean(self.focus[:self.fs])

    def getBuffer(self):
        if not LIVE_DATA: 
            self.buffer = np.roll(self.buffer, 1, 0) # To remove 
            for i in self.channels:
                self.buffer[0, i] = random.randint(-100, 100)
        return self.buffer
    def getAveragedFocus(self):  
        if not LIVE_DATA: 
            self.focus = np.roll(self.focus, 1, 0) # To remove
            self.focus[0] = random.randint(-1, 1)
            self.focus_logger.addFocusValue(self.focus[0])
            self.focus_average = np.roll(self.focus_average, 1, 0) # To remove
            self.focus_average[0] = np.mean(self.focus[:50])
        return self.focus_average

    def push_data_sample(self, sample):
        # Count the number of samples up till the full buffer (this is for mean calculation)
        if self.count_samples < self.fs * self.buffer_seconds: 
            self.count_samples += 1
        
        # Get the scaled channel data
        if self.live: 
            raw_eeg_data = np.array(sample.channels_data) * SCALE_FACTOR_EEG
        else :
            raw_eeg_data = np.array(sample) 
        
        # Roll and prepend the buffer with the new data
        self.raw_buffer = np.roll(self.raw_buffer, 1, 0)
        self.buffer = np.roll(self.buffer, 1, 0)
        self.dc_removed_buffer = np.roll(self.dc_removed_buffer, 1, 0)
        self.power_bin_values = np.roll(self.power_bin_values, 1, 0)
        self.focus = np.roll(self.focus, 1, 0)
        self.focus_average = np.roll(self.focus_average, 1, 0)
        for i, chan in enumerate(self.channels):
            self.raw_buffer[0, i] = raw_eeg_data[chan]
            if self.raw_buffer[0, i] == 0 : 
                continue
            if self.to_clean:  
                self.dc_removed_buffer[0, i] = self.raw_buffer[0,i] - self.mean[i]
                self.buffer[0, i] = self.dc_removed_buffer[0, i]
            else : 
                self.dc_removed_buffer[0, i] = self.raw_buffer[0, i] 
                self.buffer[0, i] = self.raw_buffer[0, i] 
            self.focus[0] = self.focus[1]
            self.focus_average[0] = np.mean(self.focus[:self.fs])
        
        # Calculate the new mean if the update time has passed
        now = time.time()
        if (now - self.last_updated) > self.update_seconds :
            self.last_updated = now
            if (self.count_samples > 500): 
                if (self.to_clean):
                    self.__filter_eeg()
                if (self.model is not None):
                    self.__update_focus()
        self.focus_logger.addFocusValue(self.focus[0])
                
            