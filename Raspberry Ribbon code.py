from gpiozero import LED, Motor, Button
import time
import sys
from sensor_library import *
from gpiozero import Servo

sensor = Distance_Sensor()
 
led_red = LED(5)
led_green = LED(6)
 
motorL = Motor(forward=16, backward=20)
motorR = Motor(forward=19, backward=26)
buttonL = Button(21) #left, black button
buttonR = Button(22) #right, green button
servo = Servo(8)


def read_sensor():	
    S_left = []
    S_right = []
    count1 = 0
    count2 = 0
    
    while buttonL.is_pressed: #left side
        while count1 <= 5:
            sensor_val = round(sensor.distance(), 0)
            S_left.append(sensor_val)
            print("Left side reading:", sensor_val)
            time.sleep(0.4)
            count1 += 1
        S_left_avg = sum(S_left)/len(S_left)
        print("Left side average:", S_left_avg)
        time.sleep(1) #maybe 
        return S_left_avg

    if S_left_avg > 30: #device is malfunctioning
        led_red.on()


    while buttonR.is_pressed: #right side
        while count2 <=5:
            sensor_val = round(sensor.distance(), 0)
            S_right.append(sensor_val)
            print("Right side reading:", sensor_val)
            time.sleep(0.4)
            count2 += 1
        S_right_avg = sum(S_right)/len(S_right)
        print("Left side average:", S_left_avg)
        return S_right_avg, S_right

    return None, None

 
def move_motor(motor, led, direction):
    if direction == "forward":
        motor.forward()
    else:
        motor.backward()
    time.sleep(0.2)
    motor.stop()

def left_measurement():
    buttonL.wait_for_press()
    buttonL.when_pressed = read_sensor()
    S_left_avg = read_sensor()
    return S_left_avg

def actuation():
    Servo = servo
    Servo.max()
    time.sleep(1)
    print("Arms have closed")
    
    print("Press LEFT button for reference measurement")
    reference = left_measurement()
    print("Left side distance:", reference)
    
    while reference <= 200:
        #initial actuation (together)
        motorL.forward()
        motorR.forward()
        time.sleep(2)
        motorL.stop()
        motorR.stop()

        if reference == 300: #no tightening occured after first round
            led_red.on() #(something is caught in gear, maybe hair)

        print("Press RIGHT button for right measurement")
        buttonR.wait_for_press()
        while buttonR.is_pressed:
            S_right_avg, S_right = read_sensor()
        print ("Final right side distance:", S_right_avg)

        print("Fixing right side, do not press buttons")
        S_right = round(sensor.distance(), 0)
        difference = round(S_right - reference, 0)
        while difference != 0:
            print("Updated right reading:", S_right)
            time.sleep(0.2)
            if S_right < reference:
                move_motor(motorR, ledR, "forward")
                S_right = round(sensor.distance(), 0)
            elif S_right > reference:
                move_motor(motorR, ledR, "backward")
                S_right = round(sensor.distance(), 0)
            S_right = round(sensor.distance(), 1)
            difference = round(S_right - reference, 0)

        print("Measuring left side again")
        reference = left_measurement() #updating reference for next round
            
                
    #tightening is done            
    motorL.stop()
    motorR.stop()
    led_green.on()
    Servo.min()
    led_red.off()
    time.sleep(5)
    led_green.off()
    sys.exit(0)

 
#move arms back (servo motor)
 
def main():
    while True:
        try:
            actuation()
 
        except KeyboardInterrupt:
            motorL.stop()
            motorR.stop()
            ledL.off()
            ledR.off()
            sys.exit(0)
