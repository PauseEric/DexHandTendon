from dynaMotor import *
#from init import settings
import sys, math, time
import multiprocessing as mp
from multiprocessing import Pool

HOMING_VELOCITY = 200 #velocity at which the motors will home, WILL AFFECT HOMING CURRRENT THRESHOLD
HOMING_CURENT_THRESHOLD = 180 #current threshold at which the motors will be considered homed, WILL AFFECT HOMING VELOCITY VALUE


GRAB_CURRENT_THRESHOLD = 180
MOVE_VELOCITY = -1000 #velocity at which the motors will move during normal motions 
dynamixel = DXL_Coms(deviceSerial,B_Rate)
loose= dynamixel.createMotor("loose", motor_number = 2) 
pointer = dynamixel.createMotor("pointer", motor_number = 1)
thumb = dynamixel.createMotor("thumb", motor_number = 0)
motor_name= {
    'thumb': thumb,
    'pointer': pointer, 
    'loose': loose
}
motor_ID= {
    thumb.DXL_ID: 'thumb',
    pointer.DXL_ID: 'pointer',
    loose.DXL_ID: 'loose'
}

untension_val = { #specifically for homePosition, used to decrease the tension on the tendons to prevent damage over tim
    thumb.DXL_ID: 1000, #set values tuned for each motor, will need retuning if the physical  tendons are adjustced
    pointer.DXL_ID: 3000, #^
    loose.DXL_ID: 1500 #^
}

motor_offset= {
    thumb.DXL_ID: 0,
    pointer.DXL_ID: 0,
    loose.DXL_ID: 0
}

pinch_pos= {
    thumb.DXL_ID: 2093,
    pointer.DXL_ID: 6783,
    loose.DXL_ID: motor_offset[2]
}

motor_list = [thumb, pointer, loose]

#setting motor reverse direction
pointer.reversal(True)
thumb.reversal(False)
loose.reversal(False)

print(pointer.DIRECTION)

def main():
    print("function start")
    print("Operating Dynamixel Motors")
    disableMotors()
    for motor in motor_list:
        motor.switchMode('velocity') #default control mode set to position
        motor.enableMotor()
    # for motor in motor_list:
    #     motor.switchMode('position')
    #     motor.enableMotor()
    #     dynamixel.updateMotorData()
    #     print(motor.checkOperatingMode())
    while True:
        cmd = input("Enter Command: home for homing motors, move to move motors, grab to grab object, pinch to pinch object, open to open hand, data to read all values")
        if cmd == "home":
            homeAll()
        elif cmd == "move":
            moveAll(0.5)
        elif cmd == "grab":
            grabObject(MOVE_VELOCITY)
        elif cmd == "open":
            for motor in motor_list:
                motorChangeMode(motor, "extended_position")
                goHome(motor)
        elif cmd == "pinch":
            pinchObject(-500)
        elif cmd == "data":
            print("All Data")
            print("Motor Pos:")
            for motor in motor_list:
                print(getPos(motor))
            print("Offset Values:")
            print(motor_offset)

        else:
            print("Unknown Command")


def moveAll(seconds): #For testing, once motors set to extended position control mode, DO NOT USE
    for motor in motor_list:
        motor.disableMotor()
        motor.switchMode('velocity')
        motor.enableMotor()
        motor.setVelocity(-200 * motor.DIRECTION)
    time.sleep(seconds)
    for motor in motor_list:
        motor.setVelocity(0)

def goHome(target_motor): #move motor to home position after homing, designed for multiprocessing approach, but reached permission error when trying to access motor data in multiple processes
    if target_motor.OPERATING_MODE != EXTENDED_POSITION_MODE:
        print("Operating Mode Error while moving to home position")
        return
    if target_motor.torqueEnabled == False:
        print("Torque Error while moving to home position")
        return
    target_motor.writeExtendedPosition(motor_offset[target_motor.DXL_ID])
    dynamixel.sentAllCmd()

def pinchObject(velocity): #currently unreliable due to lack of direct control over which link of the finger moves first
    motors_pinch = [False, False, True]
    for motor in motor_list:
        motorChangeMode(motor, 'extended_position')
        motor.writeExtendedPosition(pinch_pos[motor.DXL_ID])
    dynamixel.sentAllCmd()
    time.sleep(0.7)
    for motor in motor_list:
        if (motors_pinch[motor.DXL_ID] == False):
            motorChangeMode(motor, 'velocity')
            motor.setVelocity(velocity * motor.DIRECTION)
    time.sleep(0.2)
    while not all(motors_pinch):
        for motor in motor_list:
            if (abs(getCurrent(motor)) > GRAB_CURRENT_THRESHOLD and motors_pinch[motor.DXL_ID] == False):
                motor.setVelocity(0)
                motorChangeMode(motor, 'extended_position')
                print("Motor " + str(motor_ID[motor.DXL_ID]) + " reached grabbing state")
                motors_pinch[motor.DXL_ID] = True
        time.sleep(0.01)
    print("Pinched Object")

def grabObject(velocity):
    motors_grab = [False, False, False]
    for motor in motor_list:
        motorChangeMode(motor, 'velocity')
        motor.setVelocity(velocity * motor.DIRECTION)
    time.sleep(0.2)
    while not all(motors_grab):
        for motor in motor_list:
            if (abs(getCurrent(motor)) > GRAB_CURRENT_THRESHOLD and motors_grab[motor.DXL_ID] == False):
                motor.setVelocity(0)
                motorChangeMode(motor, 'extended_position')
                print("Motor " + str(motor_ID[motor.DXL_ID]) + " reached grabbing state")
                motors_grab[motor.DXL_ID] = True
        time.sleep(0.01)
    print("Grabbed Object")

def motorChangeMode(motor, mode):
    motor.disableMotor()
    motor.switchMode(mode)
    motor.enableMotor()

def homeAll():
    print("Homing All Motors")
    #Sequential Homing Approach
    motors_homed= [False, False, False]
    for motor in motor_list:
        motorChangeMode(motor, 'velocity')
        motor.setVelocity(HOMING_VELOCITY * motor.DIRECTION)
    dynamixel.updateMotorData()
    time.sleep(0.2)
    while not all (motors_homed):
        for motor in motor_list:
            if (abs(getCurrent(motor)) > HOMING_CURENT_THRESHOLD and motors_homed[motor.DXL_ID] == False):
                motor.setVelocity(0)
                motorChangeMode(motor, 'extended_position')
                print("Homing Complete for Motor: " + motor_ID[(motor.DXL_ID)])
                motors_homed[motor.DXL_ID] = True
                setMotorOffset(getPos(motor), motor) #sets a local home to keep track of this position as local zero for the motor, more readable
        time.sleep(0.01)
    dynamixel.updateMotorData()
    print("Motors Homed: " + str(motors_homed))              
    printAllPos()
    print("HOME ALL COMPLETE")
    print("Untensioning")
    for motor in motor_list:
        motor.writeExtendedPosition( motor_offset[motor.DXL_ID] - (motor.DIRECTION* untension_val[motor.DXL_ID]))
    dynamixel.sentAllCmd()
    time.sleep(2)
    printAllPos()
    print("Untensioning Complete, Rezeroing Motor Offsets")
    for motor in motor_list:
        setMotorOffset(getPos(motor), motor)
    print("Motors Rezeroed, Current Offsets (thumb, pointer, loose): " + str(motor_offset))
    print("Ready for Operations")

def printAllPos():
    for motor in motor_list:
        print(getPos(motor) - motor_offset[motor.DXL_ID]) 

def printAllRawPos():
    for motor in motor_list:
        print(getPos(motor))

def enableMotors():
    for motor in motor_list:
        motor.enableMotor()

def disableMotors():
    for motor in motor_list:
        motor.disableMotor()
    
def getCurrent(target_motor): #reads motor current parameter with adjustments for negative values
    rawCurrentVal = target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] )[0]
    if (rawCurrentVal > 32768):
        adjustedVal = rawCurrentVal - 65536
    else: 
        adjustedVal = rawCurrentVal
    return adjustedVal

def getRawCurrent(target_motor): #direct read of motor current parameter, no adjustments for negative values, used for testing and debugging purposes   
    rawCurrentVal = target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] )[0]
    return rawCurrentVal    

def getPos(target_motor):
    pos = target_motor.directReadData(target_motor.infoParam('position')[1], target_motor.infoParam('position')[2] )[0]
    if (pos > 2147483647): #adjust for negative values due to 4 byte position parameter
        pos-= 4294967296
    return pos

def getRawPos(target_motor):
    pos = target_motor.directReadData(target_motor.infoParam('position')[1], target_motor.infoParam('position')[2] )[0]
    if (pos > 2147483647): #adjust for negative values due to 4 byte position parameter
        pos-= 4294967296
    return pos

def setMotorOffset(offset, target_motor):
    motor_offset[target_motor.DXL_ID] = offset
    print("Motor Offset for " + motor_ID[target_motor.DXL_ID] + " set to: " + str(offset))


# def homeMotor(target_motor): #homing for individual motor, made for multiprocessing approach, but reached permission error when trying to access motor data in multiple processes
#     print("Homing Motor: " + str(target_motor.DXL_ID))
#     target_motor.disableMotor()
#     target_motor.switchMode('velocity')
#     target_motor.enableMotor()
#     target_motor.setVelocity(HOMING_VELOCITY * target_motor.DIRECTION)
#     time.sleep(0.2)
#     print(getCurrent(target_motor))
#     while(abs(getCurrent(target_motor)) < HOMING_CURENT_THRESHOLD): 
#         # print ("homing" + str(target_motor.directReadData(target_motor.infoParam('current'))))
#         print("looping")
#         print(getRawCurrent(target_motor))
#         print(getCurrent(target_motor))
#         print(target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] ))
#     print(getCurrent(target_motor))
#     target_motor.setVelocity(0)
#     target_motor.disableMotor()
#     target_motor.switchMode('extended_position')
#     target_motor.enableMotor()
#     print("Homing Complete for Motor: " + str(target_motor.DXL_ID))
#     print("Untensioning")



if __name__ == "__main__":
    try:
        main()  
    except KeyboardInterrupt:
        print("Keyboard Interrupt, Disabling Motors and Exiting Program")
    finally:
        
        for motor in motor_list:
            motorChangeMode(motor,'extended_position')
            goHome(motor)
            
        time.sleep(2)
        disableMotors()
