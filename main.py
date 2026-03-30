from dynaMotor import *
#from init import settings
import sys, math, time
import multiprocessing as mp
from multiprocessing import Pool

HOMING_VELOCITY = 200

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
        cmd = input("Enter Command: home for homing motors, move for moving motors in extended position control")
        if cmd == "home":
            homeAll()
        elif cmd == "move":
            moveAll(0.5)
            # loose.disableMotor()
            # loose.switchMode('velocity')
            # loose.enableMotor()
            # loose.setVelocity(-200)
            # time.sleep(1)
            # loose.setVelocity(0)
            # loose.disableMotor()

            # pointer.disableMotor()
            # pointer.switchMode('velocity')
            # pointer.enableMotor()
            # pointer.setVelocity(200)
            # time.sleep(1)
            # pointer.setVelocity(0)
            # pointer.disableMotor()

            # thumb.disableMotor()
            # thumb.switchMode('velocity')
            # thumb.enableMotor()
            # thumb.setVelocity(-200)
            # time.sleep(1)
            # thumb.setVelocity(0)
            # thumb.disableMotor

        # print(getCurrent(pointer))
        # time.sleep(0.2)
            # pos = int(input("Move to pos: "))
            # thumb.writeExtendedPosition(pos)
            # dynamixel.sentAllCmd()
            # dynamixel.updateMotorData()
            # for motor in motor_list:
            #     print(motor.checkOperatingMode())
        
        

    # print("Homing All Motors")    
    # for motor in motor_list:
    #     homeMotor(motor)

def moveAll(seconds):
    for motor in motor_list:
        motor.disableMotor()
        motor.switchMode('velocity')
        motor.enableMotor()
        motor.setVelocity(-200 * motor.DIRECTION)
    time.sleep(seconds)
    for motor in motor_list:
        motor.setVelocity(0)

def homeAll():
    print("Homing All Motors")
    #Multiprocessing approach (reached permission error, untested, logically works)
    # motors = [loose, pointer, thumb]
    
    # with Pool(processes=len(motors)) as pool:
    #     pool.map(homeMotor, motors)
    #Sequential Homing Approach
    motors_homed= [False, False, False]
    for motor in motor_list:
        motor.disableMotor()
        motor.switchMode('velocity')   
        motor.enableMotor()
        motor.setVelocity(HOMING_VELOCITY * motor.DIRECTION)
    dynamixel.updateMotorData()
    time.sleep(0.2)
    while(motors_homed != [True, True, True]):
        for motor in motor_list:
            if (abs(getCurrent(motor)) > 180 and motors_homed[motor.DXL_ID] == False):
                motor.setVelocity(0)
                motor.disableMotor()
                motor.switchMode('extended_position')
                motor.enableMotor()
                print("Homing Complete for Motor: " + motor_ID[(motor.DXL_ID)])
                motors_homed[motor.DXL_ID] = True
        time.sleep(0.01)
    dynamixel.updateMotorData()
    print("Motors Homed: " + str(motors_homed))              
    print("HOME ALL COMPLETE")


def homeMotor(target_motor): #homing for individual motor, made for multiprocessing approach, but reached permission error when trying to access motor data in multiple processes
    print("Homing Motor: " + str(target_motor.DXL_ID))
    target_motor.disableMotor()
    target_motor.switchMode('velocity')
    target_motor.enableMotor()
    target_motor.setVelocity(HOMING_VELOCITY * target_motor.DIRECTION)
    time.sleep(0.2)
    print(getCurrent(target_motor))
    while(abs(getCurrent(target_motor)) <180): 
        # print ("homing" + str(target_motor.directReadData(target_motor.infoParam('current'))))
        print("looping")
        print(getRawCurrent(target_motor))
        print(getCurrent(target_motor))
        print(target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] ))
    print(getCurrent(target_motor))
    target_motor.setVelocity(0)
    target_motor.disableMotor()
    target_motor.switchMode('extended_position')
    target_motor.enableMotor()
   
    print("Homing Complete for Motor: " + str(target_motor.DXL_ID))
 
def enableMotors():
    for motor in motor_list:
        motor.enableMotor()

def disableMotors():
    for motor in motor_list:
        motor.disableMotor()

def getCurrent(target_motor):
    rawCurrentVal = target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] )[0]
    if (rawCurrentVal > 32768):
        adjustedVal = rawCurrentVal - 65536
    else: 
        adjustedVal = rawCurrentVal
    return adjustedVal

def getRawCurrent(target_motor):
    rawCurrentVal = target_motor.directReadData(target_motor.infoParam('current')[1], target_motor.infoParam('current')[2] )[0]
    return rawCurrentVal    

if __name__ == "__main__":
    try:
        main()  
    except KeyboardInterrupt:
        print("Keyboard Interrupt, Disabling Motors and Exiting Program")
    finally:
        for motors in motor_list:
            motors.disableMotor()
        disableMotors()
