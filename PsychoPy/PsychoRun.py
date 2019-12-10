###############
### Imports ###
###############

# Allow Python 2 to run this code.
from __future__ import absolute_import, division

# psychopy imports
from psychopy.hardware import keyboard
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import random as rd

# numpy imports
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
from enum import Enum

import os  # handy system and path functions
import sys  # to get file system encoding
import textsupply as ts
from pylsl import StreamInfo, StreamOutlet
import threading
from pyOpenBCI import OpenBCICyton



sys.path.append('../')

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)


#############################
### Initialize variables ###
#############################

NUM_TO_READ = 3 # Number of articles to read. 


introductionText = "MyND: MyNeuroDetector"
instructionsText1 = "Instructions: \n\n"+\
    "Your task is to identify all words that contain the target letters. \n\n"+\
    "Press the space bar when you see a word with at least one of the target letters. \n\n"+\
    "Points++ if identified correctly\nPoints-- if incorrectly identified\n\nTry to get as many points as possible!"
calibrationText = "Calibration stage \n\nFollow the instructions that pop up, while keeping head as still as possible." 
lookHereText = "Look Here\nthen Press Space"
blinkText = "Blink twice\nthen Press Space"
closeEyeText = "Close your eyes and count to 5\n\nthen Press Space"


instructionsText2 = "There will be " + str(NUM_TO_READ) + " articles for you to read. \n\n"\
    "Each article will have different target letters.\n\n"\
    "A list of letters for you to memorize will appear next."

image_pos = (0.75, 0)
image_pos_2 = (-0.75, 0)
word_pos = (-0.4, 0)
points_pos = (0, 0.3)
PERCENT_SHOW = 0.8 # Percentage of time the text should be shown in TimedTextWithSpaceExit

SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
SCALE_FACTOR_AUX = 0.002 / (2**4)

two_memes = False

memes_path = "./pics/memes"
all_memes = os.listdir(memes_path)
meme_filenames = [os.path.join(memes_path, all_memes[i]) for i in range(len(all_memes))]
rd.shuffle(meme_filenames)

if (two_memes):
    meme_filenames2 = list(meme_filenames)
    rd.shuffle(meme_filenames2)

PSYCHO_PY_MARKERS = {
    "start": "StimStart",
    "memorizationStart": "MemorizationStart",
    "memorizationStop": "MemorizationStop",
    "newWord": "NewWord",
    "newMeme": "NewMeme",
    "spacePressed": "SpacePressed",
    "correct": "CorrectResponse", 
    "missed": "MissedResponse", 
    "incorrect": "IncorrectResponse", 
    "end": "StimEnd"
}



class FocusDistractionExperiement: 
    
    def __init__(self): 

        self.__win = None
        self.__routineTimer = None
        self.__kb = None
        self.__meme_stim = None
        self.__points_stim = None

        self.__board = None
        self.__marker_outlet = None
        self.__outlet_eeg = None
        self.__outlet_aux = None


        self.__current_meme = 0
        self.__points = 0
        self.__endExpNow = False

    def __getTextStim(self, text, location=(0,0)): 
        return visual.TextStim(win=self.__win, name='textStim',
            text=text,
            font='Arial',
            pos=location, height=0.05, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)
 
    def __getPointsStim(self): 
        self.__points_stim = visual.TextStim(win=self.__win, name='textStim',
            text="Points: 0",
            font='Arial', units='',
            pos=points_pos, height=0.02, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)
        return self.__points_stim

    def __getMemeStim(self, filename): 
        self.__meme_stim = visual.ImageStim(
            win=self.__win, name='image',
            image=filename, mask=None,
            ori=0, units='norm', pos=image_pos, size=(0.5, 0.5),
            color=[1,1,1], colorSpace='rgb', opacity=1,
            flipHoriz=False, flipVert=False,
            texRes=128, interpolate=True, depth=0.0)
        return self.__meme_stim
    
    def __getMemeStim2(self, filename): 
        self.__meme_stim2 = visual.ImageStim(
            win=self.__win, name='image',
            image=filename, mask=None,
            ori=0, units='norm', pos=image_pos_2, size=(0.5, 0.5),
            color=[1,1,1], colorSpace='rgb', opacity=1,
            flipHoriz=False, flipVert=False,
            texRes=128, interpolate=True, depth=0.0)
        return self.__meme_stim2


    def __startRoutine(self, components) :
        for thisComponent in components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED

    def __setDrawOn(self, components) :
        for stim in components :
            if stim.status == NOT_STARTED:
                stim.status = STARTED
                stim.setAutoDraw(True)
    
    def __endRoutine(self, components) :
        for thisComponent in components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
                thisComponent.status = NOT_STARTED 

    
    def __showTextWithSpaceExit(self, text, location=(0, 0), add_instr=True): 
        
        stim = self.__getTextStim(text + ("\n\n>> Press Space to advance." if add_instr else ""), location=location)
        components = [stim]
        self.__startRoutine(components)

        continueRoutine = True
        while continueRoutine:

            # *introduction* updates
            self.__setDrawOn(components)

            # Check if space pressed
            if 'space' in self.__kb.getKeys(['space'], waitRelease=True): 
                self.__marker_outlet.push_sample(["SpacePressed,"+str(location)+","+text])
                continueRoutine = False

            # Check for ESC quit 
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                self.__board.stop_stream()
                core.quit()
                sys.exit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        self.__endRoutine(components)
    def __showTimedText(self, text, seconds): 
        
        stim = self.__getTextStim(text)
        components = [stim]
        self.__startRoutine(components)

        # Initalize timer
        self.__routineTimer.reset()
        self.__routineTimer.add(seconds)

        continueRoutine = True
        while continueRoutine and self.__routineTimer.getTime() > 0:

            self.__setDrawOn(components)

            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                self.__board.stop_stream()
                core.quit()
                sys.exit()


            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        self.__endRoutine(components)
    def __showWordWithSpaceExitPoints(self, targetWord, seconds, textSupply) :
        stim = self.__getTextStim(targetWord)
        components = [stim]
        self.__startRoutine(components)
        #stim.pos = word_pos
        self.__routineTimer.reset()
        self.__routineTimer.add(seconds)

        continueRoutine = True 
        changedToBlank = False
        responded=False # to keep track of whether or not space was pressed this round
        while continueRoutine and self.__routineTimer.getTime() > 0:
            
            self.__setDrawOn(components)

            if (self.__routineTimer.getTime() < seconds * (1 - PERCENT_SHOW)) and not changedToBlank: 
                stim.text=""
                changedToBlank = True

            if (len(textSupply.files_read) > 1) and (not self.__meme_being_shown):
                print("Meme shown!!!")
                self.__setDrawOn([self.__meme_stim])
                if(two_memes):
                    self.__setDrawOn([self.__meme_stim2])
                self.__meme_being_shown = True
                
            # Check if space pressed
            if 'space' in self.__kb.getKeys(['space'], waitRelease=True): 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spacePressed"]])
                responded=True
                if textSupply.checkInSet(targetWord) :
                    self.__points += 1
                    self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["correct"]])
                    self.__points_stim.color='green'
                    self.__points_stim.text="Points: " + str(self.__points)
                    stim.color='green'
                else :
                    self.__points -= 1
                    self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["incorrect"]])
                    self.__points_stim.color='red'
                    self.__points_stim.text="Points: " + str(self.__points)
                    stim.color='red'

            
            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                self.__board.stop_stream()
                core.quit()
                sys.exit()

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        if not responded and textSupply.checkInSet(targetWord):
            self.__points -= 1
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["missed"]])
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["incorrect"]])
            self.__points_stim.text="Points: " + str(self.__points)
            self.__points_stim.color='red'

        self.__endRoutine(components)
    def __getDatafilenameAndSetupWindow(self): 
        #################
        ### Start Box ###
        #################
        psychopyVersion = '3.0.5'
        expName = 'NeuroFocus'  # from the Builder filename that created this script
        expInfo = {'participant': '', 'session': '001'}
        dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        expInfo['date'] = data.getDateStr()  # add a simple timestamp
        expInfo['expName'] = expName
        expInfo['psychopyVersion'] = psychopyVersion

        # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
        filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
        
        # An ExperimentHandler isn't essential but helps with data saving
        thisExp = data.ExperimentHandler(name=expName, version='',
            extraInfo=expInfo, runtimeInfo=None,
            savePickle=True, saveWideText=True,
            dataFileName=filename)

        ####################
        ### Window Setup ###
        ####################
        self.__win = visual.Window(
            size=(1440, 900), fullscr=True, screen=0,
            allowGUI=False, allowStencil=True,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            blendMode='avg', useFBO=True,
            units='height')
        # store frame rate of monitor if we can measure it
        expInfo['frameRate'] = self.__win.getActualFrameRate()
        if expInfo['frameRate'] != None:
            frameDur = 1.0 / round(expInfo['frameRate'])
        else:
            frameDur = 1.0 / 60.0  # could not measure, so guess
        
        return filename, thisExp
    def __createMarkerStream(self) : 
        info = StreamInfo(name='PsychoPy Markers', 
            type='Markers', channel_count=1, nominal_srate=0, 
            channel_format='string', source_id='psychopy_thread')
        outlet = StreamOutlet(info)
        return outlet

    def runPsychopy(self):
        # make the marker stream. Must do before the window setup to be able to start Lab Recorder
        self.__marker_outlet = self.__createMarkerStream()
        
  
        # Get experiement details and filename
        filename, thisExp = self.__getDatafilenameAndSetupWindow()

        # save a log file for detail verbose info
        logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

        ### ESC flag ###
        self.__endExpNow = False  # flag for 'escape' or other condition => quit the exp

        # Create some handy timers
        globalClock = core.Clock()  # to track the time since experiment started
        self.__routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine
        self.__kb = keyboard.Keyboard()

        # Show instructions
        self.__showTimedText(introductionText, 1)
        self.__showTextWithSpaceExit(calibrationText)

        LEFT_X_COORD = -0.55
        RIGHT_X_COORD = 0.55
        TOP_Y_COORD = -0.45
        BOTTOM_Y_COORD = 0.45

        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, 0), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, 0), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, TOP_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, BOTTOM_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, TOP_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, BOTTOM_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, TOP_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, BOTTOM_Y_COORD), add_instr=False)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False)
        
        self.__showTextWithSpaceExit(blinkText, add_instr=False)
        self.__showTextWithSpaceExit(closeEyeText, add_instr=False)


        self.__showTextWithSpaceExit(instructionsText1)
        self.__showTextWithSpaceExit(instructionsText2)

        experiment_components = []
        experiment_components.append(self.__getMemeStim(meme_filenames[self.__current_meme]))
        if (two_memes) :
            experiment_components.append(self.__getMemeStim2(meme_filenames2[self.__current_meme]))
        experiment_components.append(self.__getPointsStim())
        self.__startRoutine(experiment_components)

        # Create a text supplier
        textSupply = ts.TextSupplier()
        
        self.__setDrawOn([self.__points_stim])
        while (len(textSupply.files_read) < NUM_TO_READ) and (not textSupply.getAnotherArticle()): 
            # Get the article targets
            targets = textSupply.getTargets()
            targetsString = "Identify any words with these letters:"
            for target in targets:
                targetsString = targetsString + "\n\n" + target

            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memorizationStart"]])
            self.__showTextWithSpaceExit(targetsString)
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memorizationStop"]])

            # Reset the timers
            self.__routineTimer.reset()
            self.__kb.clock.reset() 
            total_time_elapsed = 0
            self.__meme_being_shown = False
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["start"]])

            while textSupply.hasNext():
                word = textSupply.getNext()

                # Starting with the second article, add one meme every 5 seconds 
                if len(textSupply.files_read) > 1 and total_time_elapsed % 5 == 0: 
                    self.__current_meme = ( self.__current_meme + 1 ) % len(meme_filenames)
                    self.__meme_stim.setImage(meme_filenames[self.__current_meme])
                    if (two_memes) :
                        self.__meme_stim2.setImage(meme_filenames2[self.__current_meme])

                    self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newMeme"]])
                    self.__marker_outlet.push_sample([meme_filenames[self.__current_meme]])
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newWord"]])
                self.__showWordWithSpaceExitPoints(targetWord=word, seconds=1, textSupply=textSupply)
                self.__points_stim.color='white'

                if (len(textSupply.files_read) > 1): 
                    total_time_elapsed += 1
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["end"]])
            self.__endRoutine([self.__meme_stim])
        # self.__endRoutine(nav_bar_stims)
        
        self.__endRoutine(experiment_components)
        self.__showTextWithSpaceExit("Points: " + str(self.__points))
        
        logging.flush()
        # make sure everything is closed down
        thisExp.abort()  # or data files will save again on exit
        self.__win.close()
        #core.quit()
    def __lsl_streamers(self, sample):
        self.__outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG)
        self.__outlet_aux.push_sample(np.array(sample.aux_data)*SCALE_FACTOR_AUX)

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

    def runSession(self): 
        self.__createEEGStream()
        self.__board = OpenBCICyton()
        eeg_thread = threading.Thread(target=self.__board.start_stream, args=(self.__lsl_streamers,))
        eeg_thread.start()

        self.runPsychopy()

        self.__board.stop_stream()
        sys.exit()
    
myExperiment = FocusDistractionExperiement() 

# Change this to runSession() in order to include the EEG data collection
myExperiment.runPsychopy()
