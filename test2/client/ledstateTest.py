import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

ledState = 26
ledInhale = 13

GPIO.setup(ledState, GPIO.OUT)
GPIO.setup(ledInhale, GPIO.OUT)

while True:
	GPIO.output(ledState, True)
	GPIO.output(ledInhale,False)
	sleep(0.5)
	GPIO.output(ledState,False)
	GPIO.output(ledInhale, True)
	sleep(0.5)
