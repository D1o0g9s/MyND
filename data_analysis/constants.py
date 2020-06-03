from imports import *
from PsychoPyConstants import * 


# Data stream types
class StreamType(Enum):
    MARKER = 'markers'
    EEG = 'eeg'
    AUX = 'aux'
    EYE = 'eye'
    EYENORM = 'eyenorm'
    LOOKING_UP = 'looking_up'
    LOOKING_RIGHT = 'looking_right'
    DATA = 'data'
    TIME = 'time'
    FS = 'fs'
    
    def getValues() :
        return [st.value for st in StreamType]

# MARKER_STREAM_TYPE = 'markers'
# EEG_STREAM_TYPE = 'eeg'
# AUX_STREAM_TYPE = 'aux'
# EYE_STREAM_TYPE = 'eye'
# EYE_NORM_STREAM_TYPE = 'eyenorm'
# DATA_STREAM_TYPE = 'data'
# TIME_STREAM_TYPE = 'time'
# FS_STREAM_TYPE = 'fs'

# For mapping to EEG data
channels = {'VEOG':0, 'HEOG':1, 'right_eeg': 6, 'left_eeg': 7}
alpha = (8, 12)
theta = (4, 7)
f_range = (0.1, 50)
f_hi = 2

# For determining eye tracker locations
PSYCHOPY_DIRECTIONS_X = {"left": LEFT_X_COORD, "right": RIGHT_X_COORD, "center":0}
PSYCHOPY_DIRECTIONS_Y = {"up":BOTTOM_Y_COORD, "down": TOP_Y_COORD, "center":0}