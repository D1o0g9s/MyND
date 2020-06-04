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

import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
 
import tkinter as tk
from tkinter import ttk
import random
LARGE_FONT= ("Verdana", 12)
style.use("ggplot")



class FocusSession: 
    def __init__(self, data_filename) :
        self.in_session = False 
        self.work_session = None 
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
        return data
    def writePastSession(self, timestamp, avg): 
        past_sessions = self.getPastSessions()
        if 'timestamp' not in past_sessions:
            past_sessions['timestamp'] = []
        if 'avg' not in past_sessions: 
            past_sessions['avg'] = []
        past_sessions['timestamp'].append(str(timestamp))
        past_sessions['avg'].append(str(avg))
        with open(self.data_filename, "w") as write_file:
            json.dump(past_sessions, write_file)


class FrameContainer(tk.Tk): 
    def __init__(self, *args, session=None, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #tk.Tk.iconbitmap(self, default="./clienticon.ico")
        tk.Tk.wm_title(self, "Focus Session")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, SessionViewer, PastViewer):

            frame = F(container, self, session)

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
        label = tk.Label(self, text="Focus Session", font=LARGE_FONT)
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

        self.label = tk.Label(self, text="Current Session", font=LARGE_FONT)
        self.label.pack(pady=10,padx=10)

        self.button_session = ttk.Button(self, text=self.session.session_start_text,
                            command=self.toggleSession)
        self.button_session.pack()
        
        self.button_back = ttk.Button(self, text="Back to Home",
                            command=lambda: self.controller.show_frame(StartPage))
        self.button_back.pack()

        self.fig = Figure(figsize=(5,5), dpi=100)
        self.a = self.fig.add_subplot(2, 1, 1)
        self.b = self.fig.add_subplot(2, 1, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=200)

        # canvas2 = FigureCanvasTkAgg(f2, self)
        # canvas2.draw()
        # canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show(self):
        print("config")
        if self.session.in_session:
            self.button_session.config(text=self.session.session_end_text)
        else : 
            self.button_session.config(text=self.session.session_start_text)
            
    def toggleSession(self):
        print("toggling")
        self.session.in_session = not self.session.in_session

        if self.session.in_session: 
            # start recording 
            self.session.work_session = WorkSession()
            self.session.work_session.start()
        else : 
            # end recording 
            self.session.work_session.end()
            # write data 
            self.session.writePastSession(self.session.work_session.timestamp, self.session.work_session.total_avg)
            # destroy
            self.session.work_session = None
        self.show() 

    def animate(self, i):
        print(i)
        xList = list(range(10))
        yList = list(xList)
        random.shuffle(yList)

        self.a.clear()
        self.a.plot(xList, yList)

        xList = list(range(10))
        yList = list(xList)
        random.shuffle(yList)
        self.b.clear()
        self.b.plot(xList, yList)

class PastViewer(tk.Frame):

    def __init__(self, parent, controller, session):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Past Session data", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()
    def show(self):
        print("past page")




session = FocusSession('./data_log.json')
app = FrameContainer(session=session)
app.mainloop()