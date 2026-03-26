from dynaMotor import *
#from init import settings
import sys, math, time
import multiprocessing as mp

HOMING_VELOCITY = 600

dynamixel = DXL_Coms(deviceSerial,B_Rate)
loose= dynamixel.createMotor("loose", motor_number = 3)
pointer = dynamixel.createMotor("pointer", motor_number = 2)
thumb = dynamixel.createMotor("thumb", motor_number = 1)
motor_name= {
    'loose': loose,
    'pointer': pointer, 
    'thumb': thumb
}
motor_list = [loose, pointer, thumb]

def main():
    print("function start")
    print("Operating Dynamixel Motors")
    disableMotors()
    for motor in motor_list:
        motor.switchMode('extended_position') #default control mode set to position
        motor.enableMotor()
    # for motor in motor_list:
    #     motor.switchMode('position')
    #     motor.enableMotor()
    #     dynamixel.updateMotorData()
    #     print(motor.checkOperatingMode())
    while True:
        cmd = input("Enter Command: home for homing motors, move for moving motors in extended position control")
        if cmd == "home":
            homeMotor(pointer)
        elif cmd == "move":
            pos = int(input("Move to pos: "))
            thumb.writeExtendedPosition(pos)
            dynamixel.sentAllCmd()
            dynamixel.updateMotorData()
            for motor in motor_list:
                print(motor.checkOperatingMode())
        
        

    # print("Homing All Motors")    
    # for motor in motor_list:
    #     homeMotor(motor)



def homeAll():
    print("Homing All Motors")
    p1 = mp.Process(target=homeMotor(loose))
    p2 = mp.Process(target=homeMotor(pointer))
    p3 = mp.Process(target=homeMotor(thumb))
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
    print("HOME ALL COMPLETE")
        
def homeMotor(target_motor):
    print("Homing Motor: " + str(target_motor.DXL_ID))
    target_motor.disableMotor()
    target_motor.switchMode('velocity')
    target_motor.enableMotor()
    target_motor.writeVelocity(HOMING_VELOCITY)
    print(target_motor.infoParam('current'))
    while(target_motor.infoParam('current')[2] < 200):
        pass
    target_motor.writeVelocity(HOMING_VELOCITY)
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

if __name__ == "__main__":
    main()  