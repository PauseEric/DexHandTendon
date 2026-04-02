import sys, math, time
import matplotlib.pyplot as plt
import numpy as np
import threading

class DataPlotter(object):
    def __init__(self, title, xAxis = "untitled", yAxis = "untitled"):
        self.TITLE = title
        self.XAXIS = xAxis
        self.YAXIS = yAxis
        # self.PLOT_X= x
        # self.PLOT_Y= y
        self.FIG, self.AX = plt.subplots()

    def style(self):
        self.AX.set_title(self.TITLE)
        self.AX.set_xlabel(self.XAXIS)
        self.AX.set_ylabel(self.YAXIS)
        self.AX.grid(True, linestyle='--', alpha=0.7)
        self.AX.axhline(0, color='black', linewidth=1) # X-axis
        self.AX.axvline(0, color='black', linewidth=1) # Y-axis
    
    def plotFunction(self, xVal, yVal, label=None):
        self.AX.plot(xVal, yVal, label = label) 
    
    def plotPoint(self, xVal, yVal, label= None, annotate = False):
        self.AX.scatter(xVal, yVal, label = label)
        if (annotate):
            self.AX.annotate(f'({xVal}, {yVal})', (xVal, yVal), textcoords="offset points", xytext=(0,10), ha='center') 

    def display(self):
        self.style()
        if self.AX.get_legend_handles_labels()[1]:
            self.AX.legend()
        plt.show()

class MathTimer: 
    def __init__(self, active = False, minimumTick = 0.1 ):
        self.TIME_ELAPSED= 0 #Time measured in seconds
        self.ACTIVE = active # Count Start Condition 
        self.TICK = minimumTick # Default tick is 0.1 seconds 
        if self.ACTIVE:
            self.start
    
    def start(self):
        self.THREAD = threading.Thread(target= self.count, daemon = True)
        self.ACTIVE = True
        self.THREAD.start()
    
    def count(self):
        while self.ACTIVE:
            time.sleep (self.TICK)
            self.TIME_ELAPSED += self.TICK
            #print(self.TIME_ELAPSED)
    
    def changeTickSpeed(self, tick): #Returns boolean depending on success
        if self.ACTIVE:
            print("Failed to Change Tick, Active Timer")
            return (False)
        self.TICK = tick
        return (True)

    def reportTime(self, printTime = False):
        if printTime:
            print (self.TIME_ELAPSED)
        return (self.TIME_ELAPSED)
    
    def pause(self, printTime = False):
        self.ACTIVE= False
        self.reportTime(printTime)
        print("Timer Stopped. Time:" + str(self.TIME_ELAPSED))

    def resume(self):
        print("Resume Counting")
        self.ACTIVE = True
        self.start()

    def reset(self):
        self.pause()
        self.TIME_ELAPSED = 0
        print("Timer Reset")

# timer = MathTimer()

# print("Timer Starting")
# timer.start()
# time.sleep(3)
# timer.pause() 
# print("stopped")
# timer.reportTime(True)



# plotter = DataPlotter("testing plot")
# plotter.plotPoint(3, 5, label="Vertex", annotate=True)
# plotter.plotPoint(1, 2, label="Intercept")
# plotter.display()