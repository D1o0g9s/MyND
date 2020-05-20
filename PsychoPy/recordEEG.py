
from pylsl import StreamInfo, StreamOutlet
from pyOpenBCI import OpenBCICyton
import numpy as np
from PsychoPyConstants import SCALE_FACTOR_EEG, SCALE_FACTOR_AUX
import sys

class EEGRecorder :

    def __init__(self): 
        self.__board = None
        self.__outlet_eeg = None
        self.__outlet_aux = None
        self.__createEEGStream()

    def __createEEGStream(self) : 
        info_eeg = StreamInfo(name='OpenBCI EEG', 
            type='EEG', channel_count=8, nominal_srate=250, 
            channel_format='float32', source_id='eeg_thread')
        info_aux = StreamInfo(name='OpenBCI AUX', 
            type='AUX', channel_count=3, nominal_srate=250, 
            channel_format='float32', source_id='aux_thread')

        self.__outlet_eeg = StreamOutlet(info_eeg)
        self.__outlet_aux = StreamOutlet(info_aux)
        # append some meta-data
        # info.desc().append_child_value("manufacturer", "OpenBCI")
        # channels = info.desc().append_child("channels")
        # for c in ["Fp1", "Fp2", "FPz", "A1"]:
        #     channels.append_child("channel")\
        #         .append_child_value("name", c)\
        #         .append_child_value("unit", "microvolts")\
        #         .append_child_value("type", "EEG")

        # next make an outlet; we set the transmission chunk size to 32 samples and
        # the outgoing buffer size to 360 seconds (max.)
        # outlet = StreamOutlet(info, 32, 360)

    def __lsl_streamers(self, sample):
        self.__outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG)
        self.__outlet_aux.push_sample(np.array(sample.aux_data)*SCALE_FACTOR_AUX)

    def runSession(self): 
        self.__createEEGStream()
        # eeg_thread = threading.Thread(target=self.__board.start_stream, args=(self.__lsl_streamers,))
        # eeg_thread.start()
        try:
            self.__board = OpenBCICyton()
            self.__board.start_stream(self.__lsl_streamers)
        except (KeyboardInterrupt, SystemExit):
            self.__board.stop_stream()
            sys.exit()
        

er = EEGRecorder()
er.runSession()