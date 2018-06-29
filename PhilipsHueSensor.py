import RPi.GPIO as GPIO
import time
import json
import requests
import datetime

GPIO.setmode(GPIO.BCM)
PIR = 22
ULTRASONIC_TRIG_PIN = 23
ULTRASONIC_ECHO_PIN = 24

hue_url = 'http://192.168.1.2/api/4gwCqha51VddB3Q0NlP7dbjvQckr4jm7wgbtYWpI/lights/9/state'

bodyLong = json.dumps({"on": True, "sat": 109, "bri": 210, "hue": 8711})
bodyAlert = json.dumps({"on": True, "sat": 254, "bri": 109, "hue": 1800})
bodyOff = json.dumps({"on": False})

GPIO.setup(ULTRASONIC_TRIG_PIN,GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO_PIN,GPIO.IN)
GPIO.setup(PIR,GPIO.IN)

def read_ultrasonic() :
    # Make sure the trigger pin is clean
    GPIO.output( ULTRASONIC_TRIG_PIN, GPIO.LOW )
    # Recommended resample time is 50ms
    time.sleep( 0.05 )
    # The trigger pin needs to be HIGH for at least 10ms
    GPIO.output( ULTRASONIC_TRIG_PIN, GPIO.HIGH )
    time.sleep( 0.02 )
    GPIO.output( ULTRASONIC_TRIG_PIN, GPIO.LOW )

    # Read the sensor
    while ( True ) :
        start = time.clock()
        if ( GPIO.input( ULTRASONIC_ECHO_PIN ) == GPIO.HIGH ) :
            break
    while ( True ) :
        diff = time.clock() - start
        if ( GPIO.input( ULTRASONIC_ECHO_PIN ) == GPIO.LOW ) :
            break
        if ( diff > 0.02 ) :
            return -1

    return int( round( diff * 17150 ) )

last_status = 0
try:
    while ( True ) :
        #print (read_ultrasonic())
        t = datetime.datetime.now()
        if ( t.hour < 20 and t.hour > 7 ) :
            body = json.dumps({"on": True, "sat": 109, "bri": 160, "hue": 8711})
        else :
            body = json.dumps({"on": True, "sat": 109, "bri": 100, "hue": 8711})
        if ( GPIO.input(PIR) ) :
            last_status = 1
            print("Motion Detected!")
            r = requests.put(hue_url, data=body)
            if (read_ultrasonic() < 30):
                print("Long Stay")
                r = requests.put(hue_url, data=bodyAlert)
                time.sleep(0.5)
                r = requests.put(hue_url, data=bodyLong)
                time.sleep(3000)
            time.sleep(1)
        elif ( not(GPIO.input(PIR)) and last_status==1 ) :
            print("waiting sensor re-read")
            time.sleep(10)
            last_status = 0
        else :
            last_status = 0
            bodyOff = json.dumps({"on": False})
            r = requests.put(hue_url, data=bodyOff)

except:
    GPIO.cleanup()
