import pandas as pd
import numpy as np
from neurodsp.timefrequency import amp_by_time
from neurodsp.spectral import compute_spectrum


class DataBrick:

    TIMESTAMP_INDEX = 'timestamp'
    RAW_VALUE_INDEX = 'raw_value'
    ATTENTION_INDEX = 'attention'
    ALPHA = (8, 12)

    def __init__(self, dataframe=None, Fs=128): 
        if dataframe is None: 
            data = dict()
            data[self.TIMESTAMP_INDEX] = list()
            data[self.RAW_VALUE_INDEX] = list()
            data[self.ATTENTION_INDEX] = list()
            self.df = pd.DataFrame.from_dict(data)
        else :
            self.df = dataframe
        self.Fs = Fs

    
    def appendDatapoint(self, timestamp, raw_value, attention): 
        newEntry = {self.TIMESTAMP_INDEX:timestamp, self.RAW_VALUE_INDEX:raw_value, self.ATTENTION_INDEX:attention}
        self.df.append(newEntry)
    
    

    def getLastSecond(self): 
        if len(self.df.index) >= self.Fs: 
            return self.df[-self.Fs:]
        else : 
            return self.df
    
    def getDF(self, lastSecond=False) : 
        if(lastSecond) :
            return self.getLastSecond()
        else :
            return self.df
        
    def getAverageAttention(self, lastSecond=False) :
        df = self.getDF(lastSecond)
        return np.mean(df[self.ATTENTION_INDEX].values)

    def getAverageRawValues(self, lastSecond=False) :
        df = self.getDF(lastSecond)
        return np.mean(df[self.RAW_VALUE_INDEX].values)
    
    def getAlphaPower(self, lastSecond=False):
        df = self.getDF(lastSecond) 
        val = amp_by_time(df[self.RAW_VALUE_INDEX].values, self.Fs, self.ALPHA, verbose=False) 
        freqs, spectrum = compute_spectrum(df[self.RAW_VALUE_INDEX].values, self.Fs)
        print(len(val))
        return val

    

    

    

        
