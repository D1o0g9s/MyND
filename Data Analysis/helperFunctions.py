from imports import *
from constants import * 
from PsychoPyConstants import *

# Load in xdf info a useable format
def loadxdf(fname, synthetic = False):
    # Load dataset from xdf and export eeg_raw, eeg_time, mrk_raw, mrk_time, channels
    streams, fileheader = pyxdf.load_xdf(fname, dejitter_timestamps=False) #ollie 9/11/2019
    
    # Create empty dict to be returned
    stream_data = {}
    
    # Seperate streams
    for stream in streams:
        stream_type = stream['info']['type'][0].lower()
        if stream_type in StreamType.getValues():
            stream_data[stream_type] = {}
            if stream_type == StreamType.EEG.value: 
                # Baseline EEG
                stream_data[stream_type][StreamType.DATA.value] = np.array(stream['time_series'])
                for channel in range(np.array(stream['time_series']).shape[1]): 
                    values = stream_data[stream_type][StreamType.DATA.value][:,channel]
                    mean = np.mean(values)
                    stream_data[stream_type][StreamType.DATA.value][:,channel] = values - mean
            else :
                stream_data[stream_type][StreamType.DATA.value] = np.array(stream['time_series'])
            stream_data[stream_type][StreamType.TIME.value] = np.array(stream['time_stamps'])
            if stream_type == StreamType.EEG.value: 
                stream_data[stream_type][StreamType.FS.value] = stream['info']['nominal_srate'][0]
        
    return stream_data

def getEEGfs(original_data):
    if StreamType.EEG.value in original_data : 
        return int(original_data[StreamType.EEG.value][StreamType.FS.value])
    else : 
        return -1

def getEYEfs(original_data): 
    if StreamType.EYE.value in original_data : 
        time_differences_eye_tracker = [original_data[StreamType.EYE.value][StreamType.TIME.value][i+1]-original_data[StreamType.EYE.value][StreamType.TIME.value][i] for i in range(len(original_data[StreamType.EYE.value][StreamType.TIME.value])-1)]
        mean_fs_eye_tracker = 1/np.mean(time_differences_eye_tracker)
        return int(mean_fs_eye_tracker)
    else :
        return -1

# Returns a new data structure that starts at start_timestamp and ends at end_timestamp (inclusive)
def epochByTime(start_timestamp, end_timestamp, data): 
    new_data = {}
    for stream_type in data: 
        new_data[stream_type] = {}
        time_series = data[stream_type][StreamType.TIME.value]
        data_series = data[stream_type][StreamType.DATA.value]
        
        indexes = np.intersect1d(np.where(time_series >= start_timestamp), np.where(time_series <= end_timestamp)) 
        #print(stream_type, indexes)
        new_data[stream_type][StreamType.TIME.value] = time_series[indexes]
        new_data[stream_type][StreamType.DATA.value] = data_series[indexes]
    
    return new_data

# Get the corresponding timestamp for a marker index
def getTimestampForMarkIndex(mrk_index, data):
    return data[StreamType.MARKER.value][StreamType.TIME.value][mrk_index]

# Return a new data structure that starts at the marker from index up to the marker to index (inclusive)
def epochByMarkIndex(mrk_from_index, mrk_to_index, data):
    
    start_timestamp = getTimestampForMarkIndex(mrk_from_index, data)
    end_timestamp = getTimestampForMarkIndex(mrk_to_index, data)
    
    return epochByTime(start_timestamp, end_timestamp, data)

# Returns the filtered EEG data by IIR Butterworth order = 2 
def filterEEG(eeg_data, fs, f_range=f_range):
    sig_filt = filt.filter_signal(eeg_data, fs, 'bandpass', f_range, filter_type='iir', butterworth_order=2)
    test_sig_filt = filt.filter_signal(sig_filt, fs, 'bandstop', (58, 62), n_seconds=0.25)
    num_nans = sum(np.isnan(test_sig_filt))
    sig_filt = np.concatenate(([0]*(num_nans // 2), sig_filt, [0]*(num_nans // 2)))
    sig_filt = filt.filter_signal(sig_filt, fs, 'bandstop', (58, 62), n_seconds=0.25)
    sig_filt = sig_filt[~np.isnan(sig_filt)]
    return sig_filt

# Returns the filtered EYE data by IIR Butterworth order = 2 
def filterEYE(eye_data, fs, f_hi=f_hi):
    return filt.filter_signal(eye_data, fs, 'lowpass', f_hi, filter_type='iir', butterworth_order=2)

# Get all the marker indexes in dictionary form
def getMarkerIndexes(original_data):
    markers = np.array(original_data[StreamType.MARKER.value][StreamType.DATA.value][:,0])
    marker_indexes = {}
    for index, marker in enumerate(markers): 
        if marker not in marker_indexes:
            marker_indexes[marker] = list()
        marker_indexes[marker].append(index)
    return marker_indexes

# Get marker stringas
def getSectionMarkerString(section_name):
    return "--"+section_name.capitalize()+"Start", "--"+section_name.capitalize()+"Stop"

def getSingleLabelMarkerString(label_name):
    return "--"+label_name[0].capitalize()+label_name[1:]

def getResponseLabelMarkerString(label_name):
    return "--"+label_name.capitalize()+"Response"

def getLabelMarkerString(label_name):
    marker = ""
    if label_name in SINGLE_LABELS:
        marker = getSingleLabelMarkerString(label_name)
    elif label_name in RESPONSE_LABELS: 
        marker = getResponseLabelMarkerString(label_name)
    else : 
        print(label_name + " not a valid label")
    return marker

# Get index of the previous and next label 

def getPreviousLabelIndex(label_to_find, max_index, original_data): 
    index = max_index
    while(index >= 0):
        if original_data[StreamType.MARKER.value][StreamType.DATA.value][index] == label_to_find:
            return index
        index -= 1
    return -1

def getNextLabelIndex(label_to_find, min_index, original_data): 
    index = min_index
    while(index < len(original_data[StreamType.MARKER.value][StreamType.DATA.value])):
        if original_data[StreamType.MARKER.value][StreamType.DATA.value][index] == label_to_find:
            return index
        index += 1
    return -1

## Get data sections

# Get all of a single section's data given the single section name
def getSectionData(section_name, original_data) :
    if section_name not in SINGLETON_SECTIONS: 
        print(section_name, " not a singleton section")
        return epochByMarkIndex(0, 0, original_data)
    start_marker, stop_marker = getSectionMarkerString(section_name)
    marker_indexes = getMarkerIndexes(original_data) 
    if start_marker not in marker_indexes or stop_marker not in marker_indexes : 
        return epochByMarkIndex(0, 0, original_data)
    return epochByMarkIndex(marker_indexes[start_marker][0], marker_indexes[stop_marker][0], original_data)
    

# Return the article section data given the section_name and article number 
def getArticleSectionData(section_name, article_number, original_data):
    if section_name not in ARTICLE_SECTIONS: 
        print(section_name, " not an article section")
        return epochByMarkIndex(0, 0, original_data)
    start_marker, stop_marker = getSectionMarkerString(section_name)
    marker_indexes = getMarkerIndexes(original_data) 
    if start_marker not in marker_indexes or stop_marker not in marker_indexes : 
        return epochByMarkIndex(0, 0, original_data)
    return epochByMarkIndex(marker_indexes[start_marker][article_number], marker_indexes[stop_marker][article_number], original_data)

# Returns all the single label data in the original data
# time_before and time_after: the number of seconds before and after each marker to return 
# Returns a list of all the data with time_before and time_after
def getTimeBoundSingleLabelData(label_name, original_data, time_before=2, time_after=2):
    marker_indexes = getMarkerIndexes(original_data)
    marker = getLabelMarkerString(label_name)
    if label_name == "":
        return [], [], []
    
    if marker not in marker_indexes: 
        return [], [], []
    sub_markers_indexes = marker_indexes[marker]
    sub_markers_times = list()
    data = list()
    for sub_markers_index in sub_markers_indexes:
        sub_markers_time = original_data[StreamType.MARKER.value][StreamType.TIME.value][sub_markers_index]
        sub_markers_times.append(sub_markers_time)
        start_time = sub_markers_time - time_before
        end_time = sub_markers_time + time_after
        data.append(epochByTime(start_time, end_time, original_data))
    return data, sub_markers_indexes, sub_markers_times

# primary_label_name is the primary label to look for. secondary_label_name is the secondary label to help bound the primary label in the front or the back. 
def getLabelBoundSingleLabelData(primary_label_name, secondary_label_name, original_data, go_backward=True):
    marker_indexes = getMarkerIndexes(original_data)
    marker_primary = getLabelMarkerString(primary_label_name)
    if primary_label_name == "":
        return [], [], []
    
    marker_secondary = getLabelMarkerString(secondary_label_name)
    if secondary_label_name == "":
        return [], [], []
    
    if marker_secondary not in marker_indexes or marker_primary not in marker_indexes: 
        return [], [], []
    
    return getMarkerBoundSingleMarkerData(marker_primary, marker_secondary, original_data, go_backward=go_backward)

def getMarkerBoundSingleMarkerData(marker_primary, marker_secondary, original_data, go_backward=True):
    marker_indexes = getMarkerIndexes(original_data)
    sub_markers_indexes = marker_indexes[marker_primary]
    sub_markers_secondary_indexes = list()
    data = list()
    for sub_markers_index in sub_markers_indexes:
        if go_backward:
            secondary_index = getPreviousLabelIndex(marker_secondary, sub_markers_index, original_data)
            data.append(epochByMarkIndex(secondary_index, sub_markers_index, original_data))
        else :
            secondary_index = getNextLabelIndex(marker_secondary, sub_markers_index, original_data)
            data.append(epochByMarkIndex(sub_markers_index, secondary_index, original_data))
        
        sub_markers_secondary_indexes.append(secondary_index)
    return data, sub_markers_indexes, sub_markers_secondary_indexes
        

def getNumSections(original_data):
    return len(getMarkerIndexes(original_data)[getSingleLabelMarkerString("newArticle")])

def getNumDistractions(original_data):
    marker_indexes = getMarkerIndexes(original_data)
    marker_string = getLabelMarkerString("lettersShown")
    if marker_string not in marker_indexes: 
        return 0 
    return len(marker_indexes[marker_string])

def getWordLengths(original_data): 
    marker_indexes = getMarkerIndexes(original_data)
    marker_string = getLabelMarkerString("newWord")
    if marker_string not in marker_indexes: 
        return []
    word_lengths = list() 
    for index in marker_indexes[marker_string] : 
        word_index = index + 2
        word = original_data[StreamType.MARKER.value][StreamType.DATA.value][word_index]
        print(word)
        word_lengths.append(len(word[0]))
    return word_lengths

def getPointsAfterEachWord(original_data): 
    marker_indexes = getMarkerIndexes(original_data)
    marker_string = getLabelMarkerString("endWord")
    if marker_string not in marker_indexes: 
        return []
    points_list = list() 
    time_list = list()
    for index in marker_indexes[marker_string] : 
        point_index = index - 1
        point = int(original_data[StreamType.MARKER.value][StreamType.DATA.value][point_index])
        points_list.append(point)
        time = float(original_data[StreamType.MARKER.value][StreamType.TIME.value][point_index])
        time_list.append(time)
    return points_list, time_list

def getElapsedTimeOfSection(original_data):
    return original_data[StreamType.MARKER.value][StreamType.TIME.value][-1] - original_data[StreamType.MARKER.value][StreamType.TIME.value][0]

def getTotalPoints(original_data):
    marker_indexes = getMarkerIndexes(original_data)
    start_marker_string = getLabelMarkerString("newWord")
    end_marker_string = getLabelMarkerString("endWord")
    start_points = int(original_data[StreamType.MARKER.value][StreamType.DATA.value][marker_indexes[start_marker_string][0] + 1])
    end_points = int(original_data[StreamType.MARKER.value][StreamType.DATA.value][marker_indexes[end_marker_string][-1] - 1])
    delta_points = end_points - start_points
    return delta_points

def getAvgCalibratedXandY(original_data) :
    calibrated_x = {}
    calibrated_y = {}

    marker_indexes = getMarkerIndexes(original_data)
    eye_fs = getEYEfs(original_data)

    for x_dir in PSYCHOPY_DIRECTIONS_X.keys():
        for y_dir in PSYCHOPY_DIRECTIONS_Y.keys(): 
            location = "("+str(PSYCHOPY_DIRECTIONS_X[x_dir])+", "+str(PSYCHOPY_DIRECTIONS_Y[y_dir])+")"
            ith = 0 if not location == "(0, 0)" else -3 # Get the third to last value if we are looking for the center location. This corresponds to the last (0,0) value in the calibration phase.
            new_data = epochByMarkIndex(marker_indexes[location][ith] - 2, marker_indexes[location][ith], original_data)
            x = new_data[StreamType.EYENORM.value][StreamType.DATA.value][:,0]
            x = filterEYE(x, eye_fs, f_hi=f_hi)
            new_data[StreamType.EYENORM.value][StreamType.DATA.value][:,0] = x
            y = new_data[StreamType.EYENORM.value][StreamType.DATA.value][:,1]
            y = filterEYE(y, eye_fs, f_hi=f_hi)
            new_data[StreamType.EYENORM.value][StreamType.DATA.value][:,1] = y
            time = new_data[StreamType.EYENORM.value][StreamType.TIME.value]
            
            # Get only the last 1/3 of time data from x
            time_range = time[-1] - time[0]
            time_range = time_range*2 / 3
            start_time = time[0] + time_range
            end_time = time[-1]

            third_data = epochByTime(start_time, end_time, new_data)
            x = third_data[StreamType.EYENORM.value][StreamType.DATA.value][:,0]
            y = third_data[StreamType.EYENORM.value][StreamType.DATA.value][:,1]

            # Append new average to calibration matricies
            avg_x = np.mean(x)
            avg_y = np.mean(y)

            if x_dir not in calibrated_x: 
                calibrated_x[x_dir] = list()
            if y_dir not in calibrated_y: 
                calibrated_y[y_dir] = list()
            calibrated_x[x_dir].append(avg_x)
            calibrated_y[y_dir].append(avg_y)
            
    # Average the eye locations
    avg_calibrated_x = {}
    avg_calibrated_y = {}
    for x_dir in calibrated_x: 
        avg_calibrated_x[x_dir] = np.mean(calibrated_x[x_dir])
    for y_dir in calibrated_y:
        avg_calibrated_y[y_dir] = np.mean(calibrated_y[y_dir])
    
    return avg_calibrated_x, avg_calibrated_y

def getLookingRightTimes(original_data, avg_calibrated_x, avg_calibrated_y, percent_distance_to_edge=(4/10)) :
    # original_data is the data you want to check for the location of looking
    # avg_calibrated_x and y are dicts that containt the eyenorm thresholds 
    # calculated from getAvgCalibratedXandY over the Calibrated period
    x_threshold_center_right = avg_calibrated_x['center'] + ((avg_calibrated_x['right'] - avg_calibrated_x['center'])*percent_distance_to_edge)
    eye_x_data=original_data[StreamType.EYENORM.value][StreamType.DATA.value][:,0]
    looking_right = [1 if val > x_threshold_center_right else 0 for i, val in enumerate(eye_x_data)]

    return looking_right

