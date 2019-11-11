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
from os import listdir
from os.path import join
import sys  # to get file system encoding
import textsupply as ts

sys.path.append('../')

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)


#############################
### Initialize variables ###
#############################
introductionText = "NeuroFocus"
instructionsText = "Memorize the initial list of words and click when the word had just appeared on the screen. \n\nYou have 10 minutes to get through the entire article. \n\nThere are XXX words to find."

notif_box_pos = (0.5, -0.4)
height_inc = 0.3
notif_box_pos_large = (notif_box_pos[0], notif_box_pos[1] + height_inc)
notif_cicle_pos = (notif_box_pos[0] - 0.2, notif_box_pos[1])
notif_text_pos = (notif_box_pos[0] - 0.1, notif_box_pos[1])
notif_num_pos = (notif_text_pos[0] + 0.1, notif_box_pos[1])
notif_box_size_small = (1, 0.1)
notif_box_size_large = (notif_box_size_small[0], notif_box_size_small[1] + height_inc * 2)

memes_path = "./pics/memes"
all_memes = listdir(memes_path)
meme_filenames = [join(memes_path, all_memes[i]) for i in range(len(all_memes))]


class FocusDistractionExperiement: 
    
    def __init__(self): 
        self.__notif_box_stim = None
        self.__meme_stim = None
        # self.__notif_stim = None
        self.__notif_circle_stim = None
        self.__notif_num_stim = None
        self.__win = None
        self.__routineTimer = None
        self.__kb = None
        self.__mouse = None
        self.__routineTimer = None

        self.__current_meme = 0
        self.__num_memes_available = 0
        self.__points = 0
        self.__endExpNow = False
    
    def __getNavBarStims(self):
        rect_stim = visual.Rect(self.__win, 
            autoLog=None, units='', lineWidth=1.5, lineColor='white', 
            lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', 
            pos=notif_box_pos, size=notif_box_size_small, ori=0.0, opacity=1.0, contrast=1.0, 
            depth=0, interpolate=True, name=None, autoDraw=False)
        
        num_stim = visual.TextStim(win=self.__win, name='textStim',
            text="0", units='',
            font='Arial',
            pos=notif_num_pos, height=0.02, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)

        circle_stim = visual.Circle(self.__win, 
            radius=0.5, edges=32, autoLog=None, units='', lineWidth=1.5, lineColor='black', 
            lineColorSpace='rgb', fillColor=[255, 0, 0], fillColorSpace='rgb', 
            pos=notif_cicle_pos, size=(0.025, 0.025), ori=0.0, opacity=1.0, contrast=1.0, 
            depth=0, interpolate=True, name=None, autoDraw=False)
        
        text_stim = visual.TextStim(win=self.__win, name='textStim',
            text="Notifications: ",
            font='Arial', units='',
            pos=notif_text_pos, height=0.02, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)
        
        self.__notif_circle_stim = circle_stim
        self.__notif_num_stim = num_stim
        self.__notif_box_stim = rect_stim
        return [rect_stim, num_stim, circle_stim, text_stim]
    
    def __getTextStim(self, text): 
        return visual.TextStim(win=self.__win, name='textStim',
            text=text,
            font='Arial',
            pos=(0, 0), height=0.05, wrapWidth=None, ori=0,
            color='white', colorSpace='rgb', opacity=1,
            languageStyle='LTR',
            depth=0.0)

    def __getImageStim(self, filename): 
            return visual.ImageStim(
                win=self.__win, name='image',
                image=filename, mask=None,
                ori=0, units='norm', pos=(0.70, -0.4), size=(0.5, 0.5),
                color=[1,1,1], colorSpace='rgb', opacity=1,
                flipHoriz=False, flipVert=False,
                texRes=128, interpolate=True, depth=0.0)

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

    def __showTextWithMouseExit(self, text): 
        
        stim = self.__getTextStim(text)
        components = [stim, self.__mouse]

        self.__startRoutine(components)
        continueRoutine = True

        while continueRoutine:

            # *introduction* updates
            self.__setDrawOn([stim])

            # Start mouse if not started
            if self.__mouse.status == NOT_STARTED:
                # keep track of start time/frame for later
                self.__mouse.status = STARTED
                prevButtonState = self.__mouse.getPressed()  # if button is down already this ISN'T a new click

            # Check if mouse pressed
            if self.__mouse.status == STARTED:  # only update if started and not finished!
                buttons = self.__mouse.getPressed()
                if buttons != prevButtonState:  # button state changed?
                    prevButtonState = buttons
                    if sum(buttons) > 0:  # state changed to a new click
                        # abort routine on response
                        continueRoutine = False

            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        self.__endRoutine(components)
    def __showTimedText(self, text, seconds): 
        
        stim = self.__getTextStim(text)
        mouse = event.Mouse(win=self.__win)

        components = [stim, mouse]

        self.__startRoutine(components)
        continueRoutine = True
        self.__routineTimer.add(seconds)
        # -------Start Routine "intro"-------
        while continueRoutine and self.__routineTimer.getTime() > 0:

            # *introduction* updates
            if stim.status == NOT_STARTED:
                stim.status = STARTED
                stim.setAutoDraw(True)

            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                core.quit()

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

        self.__endRoutine(components)
    def __showTimedTextWithMouseExitPoints(self, text, seconds, textSupply) :
        stim = self.__getTextStim(text)

        components = [stim, self.__mouse]

        self.__startRoutine(components)
        continueRoutine = True
        self.__routineTimer.add(seconds)
        while continueRoutine and self.__routineTimer.getTime() > 0:
            
            self.__setDrawOn([stim])

            # show the "you have notification image"
            if (self.__num_memes_available > 0): 
                self.__setDrawOn([self.__notif_circle_stim])
            else :
                self.__endRoutine([self.__notif_circle_stim])


            # Start mouse if not started
            if self.__mouse.status == NOT_STARTED:
                # keep track of start time/frame for later
                self.__mouse.status = STARTED
                prevButtonState = self.__mouse.getPressed()  # if button is down already this ISN'T a new click

            # Check if mouse pressed
            if self.__mouse.status == STARTED:  # only update if started and not finished!
                buttons = self.__mouse.getPressed()
                mouse_pos = self.__mouse.getPos()
                if buttons != prevButtonState:  # button state changed?
                    prevButtonState = buttons
                    
                    if sum(buttons) > 0:  # state changed to a new click
                        # Mouse click on message box
                        if self.__notif_box_stim.contains(mouse_pos):  
                            print(mouse_pos)
                            if not self.__meme_being_shown and self.__num_memes_available > 0:
                                print("Meme shown!!!")
                                self.__setDrawOn([self.__meme_stim])
                                self.__meme_being_shown = True
                                self.__num_memes_available -= 1
                                self.__notif_num_stim.setText(self.__num_memes_available)
                                self.__notif_box_stim.setSize(notif_box_size_large)
                                self.__notif_box_stim.setPos(notif_box_pos_large)
                            elif self.__num_memes_available > 0: 
                                self.__current_meme = ( self.__current_meme + 1 ) % len(meme_filenames)
                                self.__meme_stim.setImage(meme_filenames[self.__current_meme])
                                print(meme_filenames[self.__current_meme])

                                self.__num_memes_available -= 1
                                self.__notif_num_stim.setText(self.__num_memes_available)
                                self.__notif_box_stim.setSize(notif_box_size_large)
                                self.__notif_box_stim.setPos(notif_box_pos_large)
                            else: 
                                self.__endRoutine([self.__meme_stim])
                                self.__meme_being_shown = False
                                self.__notif_box_stim.setSize(notif_box_size_small)
                                self.__notif_box_stim.setPos(notif_box_pos)

                                self.__current_meme = ( self.__current_meme + 1 ) % len(meme_filenames)
                                self.__meme_stim.setImage(meme_filenames[self.__current_meme])
                                print(meme_filenames[self.__current_meme])
                                
                        else : # Mouse click to signal clicking on screen
                            # abort routine on response
                            continueRoutine = False
                            if textSupply.checkInSet(text) :
                                self.__points += 1
                            else :
                                self.__points -= 1


            # Check for ESC quit
            if self.__endExpNow or 'escape' in self.__kb.getKeys(['escape'], waitRelease=True):
                core.quit()

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.__win.flip()

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

    def run_psychopy(self):
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
        self.__mouse = event.Mouse(win=self.__win)
        self.__kb = keyboard.Keyboard()

        # Show instructions
        self.__showTextWithMouseExit(introductionText)
        self.__showTextWithMouseExit(instructionsText)


        # Reset the timers
        self.__routineTimer.reset()
        self.__kb.clock.reset()  # when you want to start the timer from


        # Show the words to memorize
        textSupply = ts.TextSupplier()
        targets = textSupply.getTargets()
        targetsString = "memorize these words in 5 seconds: "
        for target in targets:
            targetsString = targetsString + "\n\n" + target

        self.__showTimedText(targetsString, 1)

        #notif_filename = "./pics/you_have_meme.png"
        #self.__notif_stim = self.__getImageStim(notif_filename)
        self.__meme_stim = self.__getImageStim(meme_filenames[self.__current_meme])
        self.__startRoutine([self.__meme_stim])
        
        nav_bar_stims = self.__getNavBarStims()
        self.__startRoutine(nav_bar_stims)
        self.__setDrawOn(nav_bar_stims)

        self.__meme_being_shown = False
        total_time_elapsed = 0
        while textSupply.hasNext():
            word = textSupply.getNext()

            # add one meme every 5 seconds 
            if total_time_elapsed > 0 and total_time_elapsed % 5 == 0: 
                self.__num_memes_available += 1
                self.__notif_num_stim.setText(self.__num_memes_available)

            self.__showTimedTextWithMouseExitPoints(word, 1, textSupply)
            
            total_time_elapsed += 1
        
        self.__endRoutine(nav_bar_stims)
        self.__showTextWithMouseExit("Points: " + str(self.__points))
        logging.flush()
        # make sure everything is closed down
        thisExp.abort()  # or data files will save again on exit
        self.__win.close()
        #core.quit()


myExperiment = FocusDistractionExperiement() 
myExperiment.run_psychopy()