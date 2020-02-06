import copy # For copying and filtering the StreamData struct
import pyeeg
import pandas as pd
import numpy as np

from constants import * 
from helperFunctions import * 

## FILTERING ## 
def findLargestStdev(component, eeg_fs=250, verbose=True):
    # Finds the ICA component that has the largest standard dev if filtered to 1 to 5 Hz 
    max_i = 0
    max_val = 0
    for i in range(4): 
        filtered_sig = filterEEG(component[:,i], eeg_fs, (1, 5))
        std_val = np.std(filtered_sig)
        if (verbose) :
            plt.plot(filtered_sig, label=str(i) + " " + str(std_val))
        if std_val > max_val : 
            max_i = i
            max_val = std_val
    
    if (verbose) :
        plt.legend()
        plt.title("filtered signals to find blinks")
        plt.show()
    return max_i


def getCleanedSignal(original_data, verbose=True):
    active_eeg = original_data[StreamType.EEG.value][StreamType.DATA.value][:,list(channels.values())]
    eeg_time = original_data[StreamType.EEG.value][StreamType.TIME.value]

    if(verbose) : 
        line_objects = plt.plot(eeg_time, active_eeg)
        plt.legend(iter(line_objects), list(channels.keys()))
        plt.title("EEG of 2 Eye Blinks")
        plt.show()

    ica = FastICA(n_components=4)
    standardized=active_eeg
    standardized /= active_eeg.std(axis=0)
    
    S = ica.fit_transform(active_eeg)  # Reconstruct signals
    
    if(verbose):
        line_objects = plt.plot(eeg_time, S)
        plt.legend(iter(line_objects), list(range(len(line_objects))))
        plt.title("ICA Decomposition of EEG")
        plt.show()

    # Get the component with the largest standard deviation after being filtered to 1-10Hz
    max_i = findLargestStdev(S, verbose=verbose)
    
    remove_indices = [max_i]  # pretend the user selected components 0, 1, and 3
    
    cleaned_components = copy.deepcopy(S)
    # "remove" unwanted components by setting them to 0 - simplistic but gets the job done
    cleaned_components[:, remove_indices] = 0
    
    #reconstruct signal
    X_restored = ica.inverse_transform(cleaned_components)
    
    filtered_cleaned_data = copy.deepcopy(original_data)
    i = 0
    for channel in channels: 
        filtered_cleaned_data[StreamType.EEG.value][StreamType.DATA.value][:,channels[channel]] = X_restored[:,i]
        i += 1
        
    if(verbose):
        line_objects = plt.plot(eeg_time, X_restored)
        plt.legend(iter(line_objects), list(channels.keys()))
        plt.title("EEG without blinks")
        plt.show()
    
    return filtered_cleaned_data

def filterStreamStructEEG(original_data, eeg_fs=250):
    # Filters all the eeg data in a stream struct
    filtered_data = copy.deepcopy(original_data)
    for channel in channels :
        eeg_data = original_data[StreamType.EEG.value][StreamType.DATA.value][:,channels[channel]]
        sig_filt = filterEEG(eeg_data, eeg_fs)
        filtered_data[StreamType.EEG.value][StreamType.DATA.value][:,channels[channel]] = sig_filt

    return filtered_data

def signalNoisy(eeg_signal, eeg_fs=250, noise_threshold=12, verbose=True): 
    filtered_sig = filterEEG(eeg_signal, eeg_fs, (1, 5))
    std_val = np.std(filtered_sig)
    if(verbose) :
        plt.plot(filtered_sig, label=str(std_val))
        plt.title("Std of signals. Those with std >"+str(noise_threshold)+" will not be included in average")
    if(std_val < noise_threshold):
        return False
    else:
        return True

## Getting bins for pyeeg.bin_power ## 
def getIntervals(binning): 
    intervals = list()
    for i, val in enumerate(binning[:-1]): 
        intervals.append((val, binning[i+1]))
    return intervals

## plotting ## 
def plotPowerRatio(power_ratio, intervals): 
    y_pos = list(range(len(power_ratio)))
    plt.bar(y_pos, power_ratio, align='center', alpha=0.5)
    plt.xticks(y_pos, intervals)
    plt.ylabel('Power Ratio')
    plt.xlabel('Hz')
    plt.title('Power ratio of each frequency bin')
    plt.show()

def plotMultipleBarGraphs(bars, bar_width, bar_names, group_names, error_values=None, title=None, xlabel=None, ylabel=None): 
    if len(bar_names) != len(bars):
        print("group names must be same length as bars")
        return 
    # Set position of bar on X axis
    positions = list()
    positions.append(np.arange(len(bars[0])))
    for i, bar in enumerate(bars): 
        if i>0: 
            positions.append([x + bar_width for x in positions[i-1]])

    # Make the plot
    for i, pos in enumerate(positions):
        plt.bar(pos, bars[i], width=bar_width, label=bar_names[i])
    
    if error_values: 
        for i, pos in enumerate(positions):
            plt.errorbar(pos, bars[i], yerr=error_values[i], fmt='.k')
    
    # Add xticks on the middle of the group bars
    if xlabel: 
        plt.xlabel(xlabel)
    if ylabel: 
        plt.ylabel(ylabel)
    if title: 
        plt.title(title)
    plt.xticks([r + bar_width for r in range(len(bars[0]))], group_names)

    # Create legend & Show graphic
    plt.legend()
    plt.show()


## Get Data ## 

def getLeftRightEEG(list_epochs, epoch_length=700, **kwargs):
    left_data_list = list()
    right_data_list = list() 
    
    for data in list_epochs: 
        left_data = data[StreamType.EEG.value][StreamType.DATA.value][:,channels["left_eeg"]][:epoch_length]
        right_data = data[StreamType.EEG.value][StreamType.DATA.value][:,channels["right_eeg"]][:epoch_length]
        
        if(not signalNoisy(left_data, **kwargs)) :
            left_data_list.append(left_data)
        if(not signalNoisy(right_data, **kwargs)) :
            right_data_list.append(right_data) 
    return left_data_list, right_data_list     

def getPowerRatio(eeg_data, binning, eeg_fs=250):
    power, power_ratio = pyeeg.bin_power(eeg_data, binning, eeg_fs)
    return np.array(power_ratio)


def getLeftRightData(list_epochs, binning, **kwargs):
    # Returns left_average, right_average data of the list epochs
    
    left_data_list, right_data_list = getLeftRightEEG(list_epochs, **kwargs) 
    
    average_left_data = np.mean(left_data_list, axis=0)
    average_right_data = np.mean(right_data_list, axis=0)
    
    power_ratio_left = [getPowerRatio(data, binning) for data in left_data_list]
    power_ratio_right = [getPowerRatio(data, binning) for data in right_data_list]
    
    return (left_data_list, right_data_list), (average_left_data, average_right_data), (power_ratio_left, power_ratio_right)


def getFreqsAndPSD(data_list, eeg_fs=250) :
    # Gets the frequencies and psds of the data list 
    freq_to_return = 0
    psd_list_to_return = list()
    if(type(data_list) == tuple) :
        #print("tuple!")
        flattened_data_list = [item for sublist in data_list for item in sublist]
    else :
        #print("not tuple?")
        flattened_data_list = data_list
    for i in range(len(flattened_data_list)): 
        #print(flattened_data_list[i])
        freq, psd = spectral.compute_spectrum(flattened_data_list[i], eeg_fs, method='welch', avg_type='median', nperseg=eeg_fs*2)
        freq_to_return = freq
        psd_list_to_return.append(psd)
    
    psd_avg = np.mean(psd_list_to_return, axis=0)
    
    return freq_to_return, psd_list_to_return, psd_avg

def getSEM(numbers) :
    return (np.std(numbers, axis=0) * 2) / np.sqrt(len(numbers))

## Windowing ## 
def getWindows(eeg_data, eeg_fs=250, shift_length=50, window_length=1.0) : 
    # eeg_data = voltages
    # fs = sampling rate of eeg_data
    # shift_length = shift by 5 samples for each window
    # window_length = 1 second
    
    cursor = 0
    windows = list() 
    while(len(eeg_data) - cursor - int(eeg_fs * window_length) > 0):
        windows.append(eeg_data[cursor:cursor + int(eeg_fs * window_length)])
        cursor += shift_length
    return windows

def getWindowsList(df, **kwargs) : 
    windows = list() 

    if (type(df) == list) :
        #print("getWindows on list!")
        # Directly use the list as the list of EEG to get windows for
        flattened_data_list = df
        for eeg_data in flattened_data_list :
            windows.extend(getWindows(eeg_data, **kwargs))
        
    if (type(df) == tuple) :
        #print("getWindowsList on tuple!")
        # Unwrap the tuples to allow for each element to be an EEG in the list to windows for 
        flattened_data_list = [item for sublist in df for item in sublist]
        for eeg_data in flattened_data_list :
            windows.extend(getWindows(eeg_data, **kwargs))
        
    if (type(df) == pd.DataFrame) : 
        # print("getWindowsList on Dataframe! ")
        # Get each data and each right and left eeg to window
        for i, row in df.iterrows():
            data = row["data"]
            windows.extend(getWindows(data[StreamType.EEG.value][StreamType.DATA.value][:, channels['right_eeg']], **kwargs))
            windows.extend(getWindows(data[StreamType.EEG.value][StreamType.DATA.value][:, channels['left_eeg']], **kwargs))
    return np.array(windows)