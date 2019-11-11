from __future__ import print_function

import mindwave, time
from pprint import pprint

import socket,select

import time, datetime, sys

import matplotlib.pyplot as plt

import pandas as pd

import sys

secondsToSample = 10
Fs=128 # TODO: Try to get 512Hz to work
show=False

# Please provide the number of seconds to sample
if (len(sys.argv) > 1):
    secondsToSample = int(sys.argv[1])

samplepoints = Fs*secondsToSample

print("Connecting")
headset = mindwave.Headset('/dev/tty.MindWaveMobile-SerialPo')
time.sleep(2)
print("Connected!")

data = dict()
data['timestamp'] = list()
data['raw_value'] = list()
data['attention'] = list()
currentTimestamp = None
currentRawValue = None
currentAttention = None

sampled_data = dict()
sampled_data['timestamp'] = list() 
sampled_data['raw_value'] = list()
sampled_data['attention'] = list()

def on_raw(headset, rawvalue):
    (eeg, attention) = (headset.raw_value, headset.attention)
    
    ts = time.time()
    data['timestamp'].append(ts)
    data['raw_value'].append(eeg)
    data['attention'].append(attention)

    global currentTimestamp
    global currentRawValue
    global currentAttention
    currentTimestamp = ts
    currentRawValue = eeg
    currentAttention = attention

filename = './data/myRawEEG.csv'
filename_listener = './data/myRawEEG_listener.csv'

try:
    while (headset.poor_signal > 5):
        print("Headset signal noisy %d. Adjust the headset and the earclip." % (headset.poor_signal))
        time.sleep(0.1)
        
    print("Writing %d seconds output to %s" % (secondsToSample,filename))
    stime = time.time()
    headset.raw_value_handlers.append( on_raw )
    prevTime = 0
    while ((time.time()-stime)<secondsToSample):
        if headset.poor_signal > 5 :
            print("Headset signal noisy %d. Adjust the headset and the earclip." % (headset.poor_signal))

        if currentTimestamp is not None: 
            sampled_data["timestamp"].append(currentTimestamp)
            sampled_data["raw_value"].append(currentRawValue)
            sampled_data["attention"].append(currentAttention)

        timeDiff = int(time.time()-stime)
        if(timeDiff != prevTime) : 
            print("seconds elapsed: " + str(timeDiff))
            prevTime = timeDiff
        time.sleep(1/Fs)
        pass

finally:
    
    df = pd.DataFrame.from_dict(sampled_data)
    #df.sort_values(by=['timestamp'])
    df.to_csv(filename, index=False)

    df = pd.DataFrame.from_dict(data)
    df.to_csv(filename_listener, index=False)

    headset.stop()
