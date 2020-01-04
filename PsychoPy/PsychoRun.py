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
from pylsl import StreamInfo, StreamOutlet
import threading
from pyOpenBCI import OpenBCICyton
import pickle
import heapq
import textsupply as ts
from PsychoPyConstants import *


sys.path.append('../')

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

#############################
### Initialize variables ###
#############################

two_memes = False

memes_path = "./pics/memes"
leaderboard_path = "./leaderboard.csv"
all_memes = os.listdir(memes_path)
meme_filenames = [os.path.join(memes_path, all_memes[i]) for i in range(len(all_memes))]
rd.shuffle(meme_filenames)

if (two_memes):
    meme_filenames2 = list(meme_filenames)
    rd.shuffle(meme_filenames2)

class FocusDistractionExperiement: 
    
    def __init__(self): 

        self.__win = None
        self.__routineTimer = None
        self.__kb = None
        self.__meme_stim = None
        self.__points_stim = None
        self.__letters_stim = None

        self.__board = None
        self.__marker_outlet = None
        self.__outlet_eeg = None
        self.__outlet_aux = None

        self.__current_meme = 0
        self.__points = 0
        self.__endExpNow = False

    def __getTextStim(self, text, location=(0,0), height=0.05): 
        return visual.TextStim(win=self.__win, name='textStim',
            text=text,
            font='Arial',
            pos=location, height=height, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)
        
    def __getLettersStim(self, text): 
        return visual.TextStim(win=self.__win, name='textStim',
            text=text,
            font='Arial',
            pos=(0, 0.1), height=0.02, wrapWidth=None, ori=0,
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

    
    def __showTextWithSpaceExit(self, text, location=(0, 0), add_instr=True, height=0.05): 
        
        stim = self.__getTextStim(text + ("\n\n>> Press Space to advance." if add_instr else ""), location=location, height=height)
        components = [stim]
        self.__startRoutine(components)

        continueRoutine = True
        while continueRoutine:

            # *introduction* updates
            self.__setDrawOn(components)

            # Check if space pressed
            if 'space' in self.__kb.getKeys(['space'], waitRelease=True): 
                self.__marker_outlet.push_sample([str(location)])
                self.__marker_outlet.push_sample([text])
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spacePressed"]])
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

        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newWord"]])
        self.__marker_outlet.push_sample([str(self.__points)])
        self.__marker_outlet.push_sample([targetWord])
        self.__marker_outlet.push_sample([str(seconds)])

        if textSupply.checkInSet(targetWord) :
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["targetWord"]])
        else :
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["notTargetWord"]])
        correctness=False
        continueRoutine = True 
        changedToBlank = False
        responded=False # to keep track of whether or not space was pressed this round
        while continueRoutine and self.__routineTimer.getTime() > 0:
            
            self.__setDrawOn(components)

            if (self.__routineTimer.getTime() < seconds * (1 - PERCENT_SHOW)) and not changedToBlank: 
                stim.text=""
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["blank"]])
                changedToBlank = True

            if self.__meme_should_be_shown and (not self.__meme_being_shown) and (self.__points > 0 if POSITIVE_POINTS_MEMES_ONLY else True):
                print("Meme shown!!!")
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memeShown"]])
                self.__setDrawOn([self.__meme_stim])
                if(two_memes):
                    self.__setDrawOn([self.__meme_stim2])
                self.__meme_being_shown = True
            elif not self.__meme_should_be_shown and self.__meme_being_shown:
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memeHidden"]])
                self.__endRoutine([self.__meme_stim])
                self.__meme_being_shown = False

                
            # Check if space pressed
            if ('space' in self.__kb.getKeys(['space'], waitRelease=False)) and (not responded): 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spacePressed"]])
                responded=True
                if textSupply.checkInSet(targetWord) :
                    self.__points += 1
                    correctness=True
                    self.__points_stim.text="Points: " + str(self.__points)
                    stim.color='green'
                else :
                    self.__points -= 1
                    correctness=False
                    self.__points_stim.text="Points: " + str(self.__points)
                    stim.color='red'

            # Check if m pressed
            if ('m' in self.__kb.getKeys(['m'], waitRelease=False)): 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["lettersShown"]])
                self.__points -= 1
                self.__points_stim.text="Points: " + str(self.__points)
                self.__setDrawOn([self.__letters_stim])
            
            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                self.__board.stop_stream()
                core.quit()
                sys.exit()

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        if not responded : 
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spaceNotPressed"]])
            if textSupply.checkInSet(targetWord):
                correctness=False
                self.__points -= 1
                self.__points_stim.text="Points: " + str(self.__points)
            else :
                correctness=True
        if correctness: 
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["correct"]])
        else :
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["incorrect"]])
        self.__marker_outlet.push_sample([str(self.__points)])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["endWord"]])
        self.__endRoutine([self.__letters_stim])
        self.__endRoutine(components)
    def __getDatafilenameAndSetupWindow(self): 
        #################
        ### Start Box ###
        #################
        psychopyVersion = '3.0.5'
        expName = 'MyND'  # from the Builder filename that created this script
        expInfo = {'participant': '', 'session': '001'}
        dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        expInfo['date'] = data.getDateStr()  # add a simple timestamp
        expInfo['expName'] = expName
        expInfo['psychopyVersion'] = psychopyVersion

        # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
        filename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['participant'], expInfo['session'], expName, expInfo['date'])
        
        # An ExperimentHandler isn't essential but helps with data saving
        thisExp = data.ExperimentHandler(name=expName, version='',
            extraInfo=expInfo, runtimeInfo=None,
            savePickle=True, saveWideText=True,
            dataFileName=filename)

        ####################
        ### Window Setup ###
        ####################
        self.__win = visual.Window(
            size=(1430, 870), fullscr=False, screen=0,
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
        
        return filename, thisExp, expInfo
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
        filename, thisExp, expInfo = self.__getDatafilenameAndSetupWindow()

        # save a log file for detail verbose info
        logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

        ### ESC flag ###
        self.__endExpNow = False  # flag for 'escape' or other condition => quit the exp

        # Create some handy timers
        globalClock = core.Clock()  # to track the time since experiment started
        self.__routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine
        self.__kb = keyboard.Keyboard()

        # Flag the start of the Psychopy experiment
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["psychopyStart"]])

        # Show name of experiment and begin calibration
        self.__showTimedText(introductionText, 1)
        self.__showTextWithSpaceExit(calibrationText)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["calibrationStart"]])

        self.__showTextWithSpaceExit(blinkText, add_instr=False)
        self.__showTextWithSpaceExit(openEyeText, add_instr=False)
        self.__showTextWithSpaceExit(closeEyeText, add_instr=False)
        
        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, 0), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, 0), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, TOP_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, BOTTOM_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, TOP_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(RIGHT_X_COORD, BOTTOM_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, TOP_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(LEFT_X_COORD, BOTTOM_Y_COORD), add_instr=False, height=0.02)
        self.__showTextWithSpaceExit(lookHereText, location=(0, 0), add_instr=False, height=0.02)
        
        

        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["calibrationStop"]])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["instructionStart"]])
        self.__showTextWithSpaceExit(instructionsText1)
        self.__showTextWithSpaceExit(instructionsText2)
        self.__showTextWithSpaceExit(instructionsText3)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["instructionStop"]])

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
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newArticle"]])
            self.__marker_outlet.push_sample([textSupply.getArticlePath()])
            # Get the article targets
            targets = textSupply.getTargets()
            targetsString = "Identify any words with these letters by pressing 'space'\nPress 'm' to display the letters later:"
            for target in targets:
                targetsString = targetsString + "\n\n" + target

            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memorizationStart"]])
            self.__showTextWithSpaceExit(targetsString)
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memorizationStop"]])

            targetsString = ""
            for target in targets:
                if(targetsString == "") : 
                    targetsString = target
                else :
                    targetsString = targetsString + ", " + target
            self.__letters_stim = self.__getLettersStim(targetsString)
            self.__startRoutine([self.__letters_stim])


            # Reset the timers
            self.__routineTimer.reset()
            self.__kb.clock.reset() 
            total_time_elapsed = 0
            self.__meme_being_shown = False
            self.__meme_should_be_shown = False
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["responseStart"]])


            while textSupply.hasNext():
                word = textSupply.getNext()

                # Starting with the second article, add change meme every 5 seconds 
                if len(textSupply.files_read) > NUM_ARTICLES_WITHOUT_MEMES and total_time_elapsed > 5: 
                    if total_time_elapsed % 6 == 0: 
                        self.__current_meme = ( self.__current_meme + 1 ) % len(meme_filenames)
                        self.__meme_stim.setImage(meme_filenames[self.__current_meme])
                        
                        if (two_memes) :
                            self.__meme_stim2.setImage(meme_filenames2[self.__current_meme])

                        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newMeme"]])
                        self.__marker_outlet.push_sample([meme_filenames[self.__current_meme]])
                    if total_time_elapsed % 3 == 0 :
                        self.__meme_should_be_shown = not self.__meme_should_be_shown
                
                randInterval = rd.uniform(RAND_SECS_LOWERBOUND, RAND_SECS_UPPERBOUND)
                #print(randInterval)
                self.__showWordWithSpaceExitPoints(targetWord=word, seconds=randInterval, textSupply=textSupply)
                self.__points_stim.color='white'

                if (len(textSupply.files_read) > 1): 
                    total_time_elapsed += 1
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["responseStop"]])
            self.__endRoutine([self.__meme_stim])
        # self.__endRoutine(nav_bar_stims)
        
        self.__endRoutine(experiment_components)
        # Flag the end of the Psychopy experiment
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["psychopyStop"]])

        
        pointData = (-self.__points, expInfo['participant'])
        point_list = list()
        mode = 'a' if os.path.exists(leaderboard_path) else 'w'
        with open(leaderboard_path, mode) as f:
            f = f # Do nothing

        with open(leaderboard_path, 'rb+') as f:
            try : 
                point_list = pickle.load(f)
            except : 
                point_list = list()
        # print(point_list)
        with open(leaderboard_path, 'wb') as f: 
            point_list.append(pointData)
            heapq.heapify(point_list)
            pickle.dump(point_list, f, pickle.HIGHEST_PROTOCOL)
        # print(point_list)
        highest_scores = "Highest scores:"
        print(highest_scores)
        for i in range(len(point_list) if len(point_list) < 3 else 3):
            high_score = heapq.heappop(point_list)
            score_report = high_score[1] + "\t---\t" + str(-high_score[0])
            print(score_report)
            highest_scores = highest_scores + "\n" + str(i+1) + ". " + score_report

        self.__showTextWithSpaceExit("You have finished this part of the experiment.\nPlease notify your experimenter.\n\nPoints: " + str(self.__points) + "\n\n" + highest_scores)

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
myExperiment.runSession()
