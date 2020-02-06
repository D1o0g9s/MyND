class EEGRecorder :

    def __init__(self): 
        self.__board = None
        self.__outlet_eeg = None
        self.__outlet_aux = None

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
