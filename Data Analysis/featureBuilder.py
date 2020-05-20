import pandas as pd
import numpy as np
from helperFunctions import getEEGfs, checkDictionarySameLengths
from dataAnalysisFunctions import getIntervals, getPowerRatio 
from constants import StreamType, channels

class featureBuilder: 
    default_binning=[0.5, 4, 7, 12, 30]
    default_interval_names = ["delta", "theta", "alpha", "beta"]

    default_eeg_types = ['left', 'right', 'average', 'left_minus_right']
    default_power_comparisons = ['average_power', 'left_minus_right_power']
    default_stat_types = ['average_voltage', 'std_voltage', 
    'mean_first_difference', 'norm_mean_first_difference', 
    'mean_second_difference', 'norm_mean_second_difference']
    default_ratios = [(0, 3), (1, 3), (2, 3), (1, 2)] # Delta / Beta and Theta / Beta ratios

    def __init__(self, binning=default_binning,
                 interval_names=default_interval_names, eeg_types=default_eeg_types, 
                 power_comparisons=default_power_comparisons, stat_types=default_stat_types, ratios=default_ratios): 
        
        self.binning = binning
        self.intervals = getIntervals(binning)
        self.interval_names = interval_names
        
        if len(self.interval_names) != len(self.intervals):
            print("interval names must be the same length as intervals")
            raise
            
        
        self.eeg_types = eeg_types
        self.power_comparisons = power_comparisons
        self.stat_types = stat_types
        self.ratios = ratios
    
    
    def getCols(self): 
        cols = []
        for interval_name in self.interval_names: 
            for eeg_type in self.eeg_types: 
                cols.append(interval_name + " " + eeg_type)
            for power_comparison in self.power_comparisons: 
                cols.append(interval_name + " " + power_comparison)
        for r in self.ratios: 
            for eeg_type in self.eeg_types: # only left, right, average, difference
                cols.append(self.interval_names[r[0]] + "/" + self.interval_names[r[1]] + " " + eeg_type)
        for s in self.stat_types: 
            for eeg_type in self.eeg_types: # only left, right, average, difference
                cols.append(eeg_type + " " + s)
        cols.append("focused")
        return cols
    
    def appendDataToDict(self, data_object, focused, dictionary={}):
        """
            This will return a dictionary with the data_object's features appended so that the dictionary can 
            be transformed into a pandas dataframe. CAUTION, the returned dictionary will not contain any 
            keys that are not in the below cols list. 
            Features:
            1. Delta, Theta, Alpha, Beta for left, right, average, and left-right
            2. Average and Left power - right power for Delta, Theta, Alpha, Beta
            3. Delta/Beta, Theta/Beta ratios for left, right, and average
            4. Average, Standard deviation, mean of first diff, normalized mean of first diff, 
                mean of second diff, normalized mean of second diff for left, right, and average 
            Params: 
            Output: returns dictionary with the features of the data_object appended
        """
        # Initialize the columns we need, including the focus (0 or 1) column
        cols = self.getCols()

        # Clean up the dictionary and initialize any missing lists
        cleanedDictionary = {col: dictionary[col] if col in dictionary else [] for col in cols }
        if not checkDictionarySameLengths(cleanedDictionary):
            print("dictionary has misaligned inputs! Not going to add the new object")
            raise

        eeg_fs = getEEGfs(data_object)

        # Populate left and right eeg power info first
        for eeg_type in self.eeg_types[:2]: 
            eeg = data_object[StreamType.EEG.value][StreamType.DATA.value][:, channels[eeg_type+'_eeg']]
            power_ratios = getPowerRatio(eeg, self.binning, eeg_fs=eeg_fs)
            for idx, interval_name in enumerate(self.interval_names): 
                cleanedDictionary[interval_name + " " + eeg_type].append(power_ratios[idx])

            # Also populate amplitude average and std
            cleanedDictionary[eeg_type + " " + self.stat_types[0]].append(np.mean(eeg))
            cleanedDictionary[eeg_type + " " + self.stat_types[1]].append(np.std(eeg))
            # First differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[2]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[3]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]) / np.std(eeg))
            # Second differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[4]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[5]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]) / np.std(eeg))



        # Power of average
        for eeg_type in [self.eeg_types[2]]: 
            left_eeg = data_object[StreamType.EEG.value][StreamType.DATA.value][:, channels['left_eeg']]
            right_eeg = data_object[StreamType.EEG.value][StreamType.DATA.value][:, channels['right_eeg']]
            eeg = np.mean([left_eeg, right_eeg], axis=0)
            power_ratios = getPowerRatio(eeg, self.binning, eeg_fs=eeg_fs)
            for idx, interval_name in enumerate(self.interval_names): 
                cleanedDictionary[interval_name + " " + eeg_type].append(power_ratios[idx])

            # Also populate amplitude average and std
            cleanedDictionary[eeg_type + " " + self.stat_types[0]].append(np.mean(eeg))
            cleanedDictionary[eeg_type + " " + self.stat_types[1]].append(np.std(eeg))
            # First differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[2]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[3]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]) / np.std(eeg))
            # Second differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[4]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[5]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]) / np.std(eeg))


        # Power of difference
        for eeg_type in [self.eeg_types[3]]: 
            left_eeg = data_object[StreamType.EEG.value][StreamType.DATA.value][:, channels['left_eeg']]
            right_eeg = data_object[StreamType.EEG.value][StreamType.DATA.value][:, channels['right_eeg']]
            eeg = left_eeg - right_eeg
            power_ratios = getPowerRatio(eeg, self.binning, eeg_fs=eeg_fs)
            for idx, interval_name in enumerate(self.interval_names): 
                cleanedDictionary[interval_name + " " + eeg_type].append(power_ratios[idx])

            # Also populate amplitude average and std
            cleanedDictionary[eeg_type + " " + self.stat_types[0]].append(np.mean(eeg))
            cleanedDictionary[eeg_type + " " + self.stat_types[1]].append(np.std(eeg))
            # First differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[2]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[3]].append(np.mean([eeg[i] - eeg[i-1] for i in range(1, len(eeg))]) / np.std(eeg))
            # Second differences 
            cleanedDictionary[eeg_type + " " + self.stat_types[4]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]))
            cleanedDictionary[eeg_type + " " + self.stat_types[5]].append(np.mean([eeg[i] - eeg[i-2] for i in range(2, len(eeg))]) / np.std(eeg))


        # Average of left and right power 
        for power_comparison in [self.power_comparisons[0]]: 
            for idx, interval_name in enumerate(self.interval_names): 
                left_val = cleanedDictionary[interval_name + " " + self.eeg_types[0]][-1]
                right_val = cleanedDictionary[interval_name + " " + self.eeg_types[1]][-1]
                cleanedDictionary[interval_name + " " + power_comparison].append(np.mean([left_val,right_val]))


        # Diff of left and right power
        for power_comparison in [self.power_comparisons[1]]: 
            for idx, interval_name in enumerate(self.interval_names): 
                left_val = cleanedDictionary[interval_name + " " + self.eeg_types[0]][-1]
                right_val = cleanedDictionary[interval_name + " " + self.eeg_types[1]][-1]
                cleanedDictionary[interval_name + " " + power_comparison].append(left_val - right_val)


        # Ratios
        for eeg_type in self.eeg_types: 
            for r in self.ratios: 
                interval_1 = r[0]
                interval_2 = r[1]
                interval_1_val = cleanedDictionary[self.interval_names[interval_1] + " " + self.eeg_types[0]][-1]
                interval_2_val = cleanedDictionary[self.interval_names[interval_2] + " " + self.eeg_types[0]][-1]
                index = self.interval_names[interval_1] + "/" + self.interval_names[interval_2] + " " + eeg_type
                cleanedDictionary[index].append(interval_1_val / interval_2_val)

        cleanedDictionary["focused"].append(focused)
        if not checkDictionarySameLengths(cleanedDictionary):
            print("dictionary has misaligned inputs! Not going to add the new object")
            #raise

        return cleanedDictionary