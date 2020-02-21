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

import random as rd # shuffle etc

# import numpy as np # numpy imports for eeg
import os  # handy system and path functions
import sys  # to get file system encoding
import csv # To save experiment info into csv

# import pickle
# import heapq
import textsupply as ts
import leaderboard as lb
from PsychoPyConstants import *

# For LSL marker stream
from pylsl import StreamInfo, StreamOutlet

## These will be migrated to the PsychoPy file
# import threading # possibly won't need this. 
# from pyOpenBCI import OpenBCICyton


sys.path.append('../')

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

#############################
### Initialize variables ###
#############################

two_memes = False

memes_path = "./pics/memes"

all_memes = os.listdir(memes_path)
meme_filenames = [os.path.join(memes_path, all_memes[i]) for i in range(len(all_memes))]
rd.shuffle(meme_filenames)

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
        self.__last_points_list = list()
        self.__performance = 0 # num correct out of the last MAX_PREV_TO_INCLUDE. This is subtracted from the upperbound to get the duration for the next word

        #  self.__board = None
        #  self.__outlet_eeg = None
        #  self.__outlet_aux = None
        self.__marker_outlet = None

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
            color=[1,1,1], colorSpace='rgb', opacity=MEME_OPACITY,
            flipHoriz=False, flipVert=False,
            texRes=128, interpolate=True, depth=0.0)
        return self.__meme_stim
    
    def __getMemeStim2(self, filename): 
        self.__meme_stim2 = visual.ImageStim(
            win=self.__win, name='image',
            image=filename, mask=None,
            ori=0, units='norm', pos=image_pos, size=(0.5, 0.5),
            color=[1,1,1], colorSpace='rgb', opacity=MEME_OPACITY,
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
                # self.__board.stop_stream()
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
                # self.__board.stop_stream()
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

        if self.__meme_should_be_shown and (not self.__meme_being_shown) and (self.__points > 0 if POSITIVE_POINTS_MEMES_ONLY else True):
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memeShown"]])
            self.__setDrawOn([self.__meme_stim])
            self.__meme_being_shown = True
        elif not self.__meme_should_be_shown and self.__meme_being_shown:
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memeHidden"]])
            self.__endRoutine([self.__meme_stim])
            self.__meme_being_shown = False

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
                
            # Check if space pressed
            if ('space' in self.__kb.getKeys(['space'], waitRelease=False)) and (not responded): 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spacePressed"]])
                responded=True
                if textSupply.checkInSet(targetWord) :
                    self.__points += 1
                    self.__last_points_list.append(1)
                    correctness=True
                    self.__points_stim.text="Points: " + str(self.__points)
                    # stim.color='green'
                else :
                    self.__points -= 1
                    self.__last_points_list.append(-1)
                    correctness=False
                    self.__points_stim.text="Points: " + str(self.__points)
                    # stim.color='red'

            # Check if m pressed
            if ('m' in self.__kb.getKeys(['m'], waitRelease=False)): 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["lettersShown"]])
                # self.__points -= 1
                # self.__points_stim.text="Points: " + str(self.__points)
                self.__setDrawOn([self.__letters_stim])
            
            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                # self.__board.stop_stream()
                core.quit()
                sys.exit()

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        if not responded : 
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["spaceNotPressed"]])
            if textSupply.checkInSet(targetWord):
                correctness=False
                self.__last_points_list.append(-1)
                self.__points -= 1
                self.__points_stim.text="Points: " + str(self.__points)
            else :
                self.__last_points_list.append(0)
                correctness=True

        if len(self.__last_points_list) >= MAX_PREV_TO_INCLUDE:
            self.__last_points_list.pop(0)
            self.__performance = sum(self.__last_points_list) / MAX_PREV_TO_INCLUDE

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
        expInfo['runType'] = run_type
        expInfo['numArticles'] = NUM_TO_READ
        expInfo['numArticlesWithoutMemes'] = NUM_ARTICLES_WITHOUT_MEMES

        # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
        filename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['participant'], expInfo['session'], expName, expInfo['date'])
        
        # Save the experiment meta data to a csv file
        with open(filename+'.csv', 'w') as f:  # Just use 'w' mode in 3.x
            w = csv.writer(f)
            w.writerow(expInfo.keys())
            w.writerow(expInfo.values())

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
        # logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

        ### ESC flag ###
        self.__endExpNow = False  # flag for 'escape' or other condition => quit the exp

        # Create some handy timers
        globalClock = core.Clock()  # to track the time since experiment started
        self.__routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine
        self.__kb = keyboard.Keyboard()

        experiment_components = []
        experiment_components.append(self.__getMemeStim(meme_filenames[self.__current_meme]))
        random_start_meme_list_2 = rd.randint(0, len(meme_filenames2) - 1)
        experiment_components.append(self.__getMemeStim2(meme_filenames2[random_start_meme_list_2]))
        experiment_components.append(self.__getPointsStim())
        self.__startRoutine(experiment_components)


        # Flag the start of the Psychopy experiment
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["psychopyStart"]])


        # Show name of experiment and begin calibration
        self.__showTimedText(introductionText, 1)
        
        self.__showTextWithSpaceExit(calibrationText)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["calibrationStart"]])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["blinkStart"]])
        self.__showTextWithSpaceExit(blinkText, add_instr=False)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["blinkEnd"]])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["openEyeStart"]])
        self.__showTextWithSpaceExit(openEyeText, add_instr=False)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["openEyeEnd"]])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["closeEyeStart"]])
        self.__showTextWithSpaceExit(closeEyeText, add_instr=False)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["closeEyeEnd"]])
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["relaxStart"]])
        self.__showTextWithSpaceExit(relaxText, add_instr=False)
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["relaxEnd"]])
        self.__showTextWithSpaceExit("Enjoy These Memes\n\npress space to advance through", add_instr=False)
        for i in range(3) :
            self.__setDrawOn([self.__meme_stim2])
            self.__showTextWithSpaceExit("", add_instr=False)
            self.__endRoutine([self.__meme_stim2])
            random_start_meme_list_2 = ( random_start_meme_list_2 + 1 ) % len(meme_filenames)
            self.__meme_stim2.setImage(meme_filenames2[random_start_meme_list_2])


        if(CALIBRATE_EYE) :
            self.__showTextWithSpaceExit(calibrationText)
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
            ## CAUTION: data analysis uses the -3rd "(0, 0)" to calibrate for center looking eyes. 
        
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["calibrationStop"]])
        if (SHOW_INTRO) :
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["instructionStart"]])
            self.__showTextWithSpaceExit(instructionsText1)
            self.__showTextWithSpaceExit(instructionsText2)
            self.__showTextWithSpaceExit(instructionsText3)
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["instructionStop"]])

        # Create a text supplier
        textSupply = ts.TextSupplier(articles_path)
        
        self.__setDrawOn([self.__points_stim])
        while (len(textSupply.files_read) < NUM_TO_READ) and (not textSupply.getAnotherArticle()): 
            num_read = len(textSupply.files_read)
            to_meme = TO_MEME_OR_NOT_TO_MEME[(num_read-1) % len(TO_MEME_OR_NOT_TO_MEME)]

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
            time_shown = 0
            self.__meme_being_shown = False
            self.__meme_should_be_shown = False
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["responseStart"]])
            secs_to_show = NUM_SECONDS_SHOW_MEME

            while textSupply.hasNext():
                word = textSupply.getNext()

                # If there are supposed to be memes for this article... 
                if to_meme != 0: 
                    self.__meme_should_be_shown = True
                    time_shown += 1
                    # If shown for long enough, change meme
                    if time_shown > secs_to_show: 
                        self.__current_meme = ( self.__current_meme + 1 ) % len(meme_filenames)
                        self.__meme_stim.setImage(meme_filenames[self.__current_meme])
                        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["newMeme"]])
                        self.__marker_outlet.push_sample([meme_filenames[self.__current_meme]])

                        time_shown = 0 

                else : 
                    self.__meme_should_be_shown = False
                
                num_secs = int((RAND_SECS_STARTBOUND - self.__performance) * 10) / 10 #rd.uniform(RAND_SECS_LOWERBOUND, RAND_SECS_UPPERBOUND)
                num_secs = RAND_SECS_LOWERBOUND if num_secs < RAND_SECS_LOWERBOUND else num_secs
                self.__showWordWithSpaceExitPoints(targetWord=word, seconds=num_secs, textSupply=textSupply)
    
            # Meme was previously shown
            if self.__meme_should_be_shown: 
                self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["memeHidden"]])
                self.__endRoutine([self.__meme_stim])
                self.__meme_being_shown = False
                self.__meme_should_be_shown = False
            self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["responseStop"]])
            self.__endRoutine([self.__meme_stim])
        
        self.__endRoutine(experiment_components)

        # Flag the end of the Psychopy experiment
        self.__marker_outlet.push_sample([PSYCHO_PY_MARKERS["psychopyStop"]])

        # Show leaderboard
        leaderboard = lb.Leaderboard(3) 
        leaderboard.update(self.__points, expInfo['participant'])
        highest_scores_text = leaderboard.getHighscoresText()
        self.__showTextWithSpaceExit("You have finished this part of the experiment.\nPlease notify your experimenter.\n\nPoints: " + str(self.__points) + "\n\n" + highest_scores_text)

        logging.flush()
        # make sure everything is closed down
        thisExp.abort()  # or data files will save again on exit
        self.__win.close()

    
myExperiment = FocusDistractionExperiement() 
myExperiment.runPsychopy()
