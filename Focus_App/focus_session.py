# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

# ../ to import path; and search ../ first
import os
os.chdir("../")

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from helper_scripts.helperFunctions import loadPickle # had to change imports to use Qt4Agg

os.chdir("./Focus_App/")

from work_session import WorkSession

import json
import time

import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
 
import tkinter as tk
from tkinter import ttk
import random
LARGE_FONT= ("Verdana", 12)
BOLD_FONT= ("Verdana", 12, 'bold')
UNDERLINE_FONT = ("Verdana", 12, 'underline')

style.use("ggplot")



class FocusSession: 
    def __init__(self, data_filename) :
        self.in_session = False 
        self.work_session = WorkSession() 
        self.data_filename = data_filename 

        # Ensure file is created
        mode = 'a' if os.path.exists(self.data_filename) else 'w'
        # Create file if does not exist
        with open(self.data_filename, mode) as f:
            f = f # Do nothing
        
        self.session_start_text = "Start Session"
        self.session_end_text = "End Session"
    def getPastSessions(self): 
        data = None
        with open(self.data_filename) as json_file:
            data = json.load(json_file)
        if 'timestamp' not in data:
            data['timestamp'] = []
        if 'avg' not in data: 
            data['avg'] = []
        if 'duration' not in data:
            data['duration'] = []
        return data
    def writePastSession(self, timestamp, avg, duration_string): 
        past_sessions = self.getPastSessions()
        past_sessions['timestamp'].append(timestamp.strftime("%m/%d/%y %H:%M"))
        past_sessions['avg'].append('{:.4f}'.format(avg))
        past_sessions['duration'].append(duration_string)
        with open(self.data_filename, "w") as write_file:
            json.dump(past_sessions, write_file)


class FrameContainer(tk.Tk): 
    def __init__(self, *args, session=None, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #tk.Tk.iconbitmap(self, default="./clienticon.ico")
        tk.Tk.wm_title(self, "Focus Session")
        tk.Tk.minsize(self, 700, 700)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, SessionViewer, PastViewer):

            frame = F(container, self, session)
            #frame['padx'] = 100
            self.frames[F] = frame
            

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.show()
        frame.tkraise()

    
class StartPage(tk.Frame):

    def __init__(self, parent, controller, session):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Focus Session", font=BOLD_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Current Session",
                            command=lambda: controller.show_frame(SessionViewer))
        button.pack()

        button2 = ttk.Button(self, text="Past Sessions",
                            command=lambda: controller.show_frame(PastViewer))
        button2.pack()

    def show(self):
        print("start page")

class SessionViewer(tk.Frame):

    def __init__(self, parent, controller, session):
        tk.Frame.__init__(self, parent)
        

        self.session = session 
        self.controller = controller

        self.label = tk.Label(self, text="Current Session", font=BOLD_FONT)
        self.label.pack(pady=10,padx=10)

        self.label_avg_focus = tk.Label(self, text="Avg Focus: \t", font=LARGE_FONT)
        self.label_avg_focus.pack(pady=10,padx=10)

        self.label_duration = tk.Label(self, text="Session Duration: \t", font=LARGE_FONT)
        self.label_duration.pack(pady=10,padx=10)

        self.button_session = ttk.Button(self, text=self.session.session_start_text,
                            command=self.toggleSession)
        self.button_session.pack()
        
        self.button_back = ttk.Button(self, text="Back to Home",
                            command=lambda: self.controller.show_frame(StartPage))
        self.button_back.pack()
        self.x_values = np.linspace(0, self.session.work_session.buffer_seconds, self.session.work_session.fs * self.session.work_session.buffer_seconds)

        self.fig = Figure(figsize=(5,5), dpi=100)
        
        self.average_focus_plot = self.fig.add_subplot(2, 1, 1)
        self.average_focus_plot.set_ylim(-2, 2)
        self.average_focus_plot.set_xlim(0, self.session.work_session.buffer_seconds)
        self.average_focus_plot.set_title("Focus Value")
        self.average_focus_plot.set_ylabel("min (-1)   max (1)")
        self.average_focus_plot.set_xticklabels([])
        self.eeg_plot = self.fig.add_subplot(2, 1, 2)
        self.eeg_plot.set_ylim(-400, 400)
        self.eeg_plot.set_xlim(0, self.session.work_session.buffer_seconds)
        self.eeg_plot.set_title("EEG Data")
        self.eeg_plot.set_xlabel("Time before now (s)")
        self.eeg_plot.set_ylabel("Voltage (uV)")

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas_tk_wid = self.canvas.get_tk_widget()
        self.canvas_tk_wid.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=100)

        # canvas2 = FigureCanvasTkAgg(f2, self)
        # canvas2.draw()
        # canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show(self):
        if self.session.in_session:
            self.button_session.config(text=self.session.session_end_text)
        else : 
            self.button_session.config(text=self.session.session_start_text)
            
    def toggleSession(self):
        self.session.in_session = not self.session.in_session

        if self.session.in_session: 
            # start recording 
            self.session.work_session.start()
           
        else : 
            # end recording 
            self.session.work_session.end()
            # self.ani.event_source.stop()
            # write data 
            self.session.writePastSession(self.session.work_session.getTimestamp(), self.session.work_session.getTotalAvg(), self.session.work_session.getDuration())
        self.show() 
    
    def __plotMultilines(self, ax, xvals, yvals): 
        if ax.lines: 
            #ax.clear()
            for i, line in enumerate(ax.lines):
                line.set_ydata(yvals[i])
        else:
            #ax.clear()
            for i, ys in enumerate(yvals): 
                ax.plot(xvals, ys)
        
    def animate(self, i):        
        if self.session.work_session.started: 
            xList = self.x_values
            yList = np.transpose(self.session.work_session.getEEGBufferData())
            
            self.__plotMultilines(self.eeg_plot, xList, yList)

            xList = self.x_values
            yList = np.array([self.session.work_session.getAveragedFocusBufferData()])
            self.__plotMultilines(self.average_focus_plot, xList, yList)

            self.label_avg_focus.config(text="Avg Focus: " + '{:.4f}'.format(self.session.work_session.getTotalAvg()))
            self.label_duration.config(text="Session Duration: " + self.session.work_session.getDuration())

class PastViewer(tk.Frame):

    def __init__(self, parent, controller, session):
        tk.Frame.__init__(self, parent)
        self.session = session
        label = tk.Label(self, text="Past Session data", font=BOLD_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        label = tk.Label(self, text="#\tStart Time   \tDuration\tAverage", font=UNDERLINE_FONT)
        label.pack(pady=10,padx=10)

        self.rows=[]

    def __zipSort(self, *args):
        C = list(zip(*args))
        C = sorted(C)
        return zip(*C)
    
    def show(self):
        print("past page")
        for row in self.rows: 
            row.destroy()
        self.rows=[]
        if len(self.rows) == 0: 
            past_sessions = self.session.getPastSessions()
            float_avg = [float(v) for v in past_sessions['avg']]
            past_sessions['avg'], past_sessions['timestamp'], past_sessions['duration'] = self.__zipSort( float_avg, past_sessions['timestamp'], past_sessions['duration'])
            count = 0
            for i in range(len(past_sessions['avg']) - 1, -1, -1): 
                if count > 5:
                    break
                count += 1
                row = tk.Label(self, text=str(count) + ".\t" + past_sessions['timestamp'][i] + "\t" + past_sessions['duration'][i] + "\t" + '{:.4f}'.format(past_sessions['avg'][i]), font=LARGE_FONT)
                row.pack(pady=10,padx=10)
                self.rows.append(row)
                
                


session = FocusSession('./data_log.json')
app = FrameContainer(session=session)
app.mainloop()