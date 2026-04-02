from dynaMotor import *
from plotter import *
import threading
#from init import settings
import sys, math, time


#Motor Related Initialization
HOMING_VELOCITY = 200 #velocity at which the motors will home, WILL AFFECT HOMING CURRRENT THRESHOLD
HOMING_CURENT_THRESHOLD = 180 #current threshold at which the motors will be considered homed, WILL AFFECT HOMING VELOCITY VALUE
GRAB_CURRENT_THRESHOLD = 180
MOVE_VELOCITY = -1000 #velocity at which the motors will move during normal motions 
dynamixel = DXL_Coms(deviceSerial,B_Rate)
loose= dynamixel.createMotor("loose", motor_number = 2) 
pointer = dynamixel.createMotor("pointer", motor_number = 1)
thumb = dynamixel.createMotor("thumb", motor_number = 0)

#setting motor reverse direction
pointer.reversal(True)
thumb.reversal(False)
loose.reversal(False)
thumbPlot = DataPlotter("Thumb Current Plot")
pointerPlot = DataPlotter("Pointer Current Plot")
loosePlot = DataPlotter("Loose Finger Current Plot")

timer = MathTimer()
def settings():
    print("Settings for Dynamixel Motors")
    print("Home the Dexterous Claw Before Starting Operations")
    ##
    #System Utilizes Dynamixel XL-430 Motors
