import time
import serial
import struct
from time import sleep

import socket
from timeout import timeout #a DIY timer
import RPi.GPIO as  GPIO

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

GPIO.setwarnings(False)

#for sensor via mcp3008
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

GPIO.setmode(GPIO.BCM)

#This the remote IP address to send the data too
#HOST = '192.168.0.145'
HOST = 'localhost'
#This is the port the remove server is listening on
PORT = 10002

# Create the socket and connect to the remote server.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#This is the port number the TransPort listens for data on and 
#accepts any IP address
s.bind(('', 10001))

#relay
pinState = 4
pinInhale = 23

#led
ledState = 26
ledInhale = 13

#relaies for controlling valves
GPIO.setup(pinState,GPIO.OUT)  #relay for breathing state
GPIO.setup(pinInhale,GPIO.OUT) #relay for lost packets
GPIO.setup(ledState, GPIO.OUT)
GPIO.setup(ledInhale,GPIO.OUT)

try:
        ser = serial.Serial("/dev/ttyACM0",9600)
        time.sleep(2) # it needs a delay for the serial connection
except:
        ser = serial.Serial("/dev/ttyACM1",9600)
        time.sleep(2)


fh=open("number.txt","r") #load the number from a txt file
num = fh.readline()
print num
fh.close()

# timer for inhaling duration
class TimeCount:
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0
    def __add__(self,  other):
        together = self.secs + other.secs
        return 'total' % together
    def __repr__(self):
        ret = getattr(self,  'secs',  'not started yet')
        if isinstance(ret,  float):
            return 'total running' % ret
        return ret
    def start(self):
        self.start_time = time.time()
        self.secs = 'call stop() first'
        print('started')
    def stop(self):
        if self.start_time == 0:
            print('call start() first')
        else:
            self.stop_time = time.time()
            self.secs = self.stop_time - self.start_time
            self.__init__()


timer = TimeCount()
state = 'defalut'
stateCheck = True
inhaled = False # can not continuously inhale
maxV = 0  #sensor , max airflow strenth
capacity = 0 #raw number get from sensor
strCapacity = ''
lostCounter = 0 #counting the lost packets of each round
duration = 0
tStart = 0
tEnd =0
init = True # should start from inhale
packetState = []
udpState = 'standby'
unit = 300 #inhaling unit, will use it to divide the total capacity, it controls the inhaling length/running time
unitRounds = 0 #number of inhaling rounds per one data flow 
unitCounter = 0 


resetTimerstart = 0
resetTimerend = 0
resetTimer = 0

n = 0

#init to reset all data and settings
def reset():
	global inhaled
	global init
	global state
	global stateCheck
	global maxV
	global capacity
	global strCapacity
	global lostCounter
	global duration
	global tStart
	global tEnd
	global packetState
	global udpState
	global unitRounds
	global unitCounter
	global resetTimerstart
	global resetTimerend
	global resetTimer
	global n

	if inhaled:
		if int(strCapacity) > 0:

		        f = open("number.txt","w")
       			f.truncate()
		        f.write(str(strCapacity))
		        f.close()
	print 'saved'	
	state = 'defalut'
	stateCheck = True
	inhaled = False # can not continuously inhale
	maxV = 0  #sensor , max airflow strenth
	capacity = 0 #raw number get from sensor
	strCapacity = ''
	lostCounter = 0 #counting the lost packets of each round
	duration = 0
	tStart = 0
	tEnd =0
	init = True # should start from inhale
	capacity = 0
	packetState = []
	udpState = 'standby'
	unitRounds = 0 #number of inhaling rounds per one data flow 
	unitCounter = 0


	resetTimerstart = 0
	resetTimerend = 0
	resetTimer = 0

	n=0

	fh=open("number.txt","r") #load the number from a txt file
	num = fh.readline()
	print num
	fh.close()
	
	for i in range(10):
		GPIO.output(ledInhale,True)
		GPIO.output(ledState,True)
		sleep(0.2)
		GPIO.output(ledInhale,False)
		GPIO.output(ledState,False)
		sleep(0.2)

	sleep(0.5)
	GPIO.output(ledState,True)
	print 'reset done'
	sleep(1)


@timeout(5) # 3seconds timer
def sendPackets():
	print 'sendpacket function'
        for i in range(capacity):
                if packetState[i] == True:
                        packetState[i] = False
                        message = str(i)
                        # Send data to the server.
                        s.sendto(message, (HOST, PORT))
			print "sent", i
        global udpState
        udpState = 'sent'
	global unitCounter
	global n
	unitCounter = 0
	n = 0
        print udpState,'def sendPackets()'
        while True:
                data, addr = s.recvfrom(4096)
                #print "get" , data
                index = int(data)
                packetState[index] = True
                print packetState[index], data



def valveInhaling():
	global n
	global unitCounter
	global inhaled
	global lostCounter
	global strCapacity
        for i in range(unit):
		print 'valving'###################################################################
                if packetState[unitCounter*unit+i] == True:
                        GPIO.output(pinInhale,True)
                        GPIO.output(ledInhale,True)
                        print packetState[unitCounter*unit+i], n
                        sleep(0.05)
                else:
                        GPIO.output(pinInhale,False)
                        GPIO.output(ledInhale,False)
                        print packetState[unitCounter*unit+i], n
                        sleep(0.05)
			lostCounter = lostCounter+1
			strCapacity = str(int(num) + lostCounter)
			sendNumLed() # send number to arduino led
		n=n+1
	unitCounter = unitCounter+1
	global udpState, init, stateCheck, state
        state = 'standby'
	stateCheck = True
	if (unitCounter+1) > unitRounds:
		udpState = 'ready'
	print 'valve play done',n,'.' ,unitCounter,'round done'
	sleep(3)
	init = False
	inhaled = True
	GPIO.output(ledState,False)
	global resetTimerstart
	resetTimerstart = time.time()
	
	GPIO.output(ledInhale,False)

def checkState():
	global state
	global stateCheck
	global tStart
	global inhaled
	value = mcp.read_adc_difference(0)
	if value > 900:
                state = 'blow'
		global stateCheck
		stateCheck = False
		inhaled = False
		print 'stateCheck >900' ,value
		GPIO.output(pinState,True)
		GPIO.output(ledState,False)

	elif value < 700:
                state = 'inhale'
		global stateCheck
                stateCheck = False
                print 'stateCheck <700', value
                maxV = value
                tStart = time.time()
		GPIO.output(pinState,False)
		
	else:
                state = 'standby'
                print 'listening',value
		global stateCheck
		stateCheck = True
		GPIO.output(pinState,True)
                               
def sendNumLed(): #function that send the number to led
        reversedNum =str(strCapacity)[::-1] #reverse the string of number
        if 16-len(reversedNum) > 0:
                for i in range(16-len(reversedNum)):
                        reversedNum = reversedNum + '0'
        for i in range(len(reversedNum)): # send digits to the led one by one
                ser.write(struct.pack('>B',int(reversedNum[i])))

strCapacity = num
sendNumLed()
sleep(2)
GPIO.output(ledState,True)
GPIO.output(ledInhale,False)

if __name__ == "__main__":
	while True:
		value = mcp.read_adc_difference(0)
		#sleep(0.1)

		#checking the breathing state
		if stateCheck:
			checkState()
        		
		#main state machine	
		if state == 'inhale':
			print value ,'inhaling', udpState

#			sleep(1)
			if inhaled:
				checkState()
				global resetTimerstart
				resetTimerstart = time.time()
			else:
				if init:
					print 'inhaling'
					sleep(0.05)
                        	        if maxV < value:
                                	        maxV = value
						print 'get maxspeed: ', maxV
	                                if value > 700:
        	                                print 'inhale end'
						global tEnd
                	                        tEnd = time.time()
						global duration
                        	                duration = tEnd - tStart
						global capacity
						print 'maxspeed: ', maxV,'started at: ', tStart, 'ended at: ', tEnd, 'duration: ' , duration
	                                        sleep(1)###############################################
						capacity = int(duration * maxV)/3
	                                        print 'capacity' , capacity
						sleep(1)###################### delet later
						global unitRounds
						unitRounds = capacity/unit
						print 'will inhale', unitRounds, 'rounds'
						sleep(5) ################################# will be deleted
                	                        stateCheck = True
						if capacity <unit:
							pass
						else:
							init = False
							for i in range(capacity):
				               			 packetState.append(True)
							udpState = 'ready'
						global inhaled
						inhaled = True
						global resetTimerstart
						resetTimerstart= time.time()


				else:
					valveInhaling()


			
		elif state == 'blow':
			print 'blow',value
			if udpState == 'sent':
				
				if value <900:

					stateCheck = True
					GPIO.output(ledState,True)
				else:
					global resetTimerstart
					resetTimerstart = time.time()
					

			else:
				if init:
					if value < 900:

						stateCheck = True
						GPIO.output(ledState,True)
				
				else:
					try:
						sendPackets()
					except:
						print 'recvtimeoooooooooooout'
						time.sleep(2)
						stateCheck = True
						GPIO.output(ledState,True)

                        global resetTimerstart
                        resetTimerstart = time.time()

						

		elif state == 'standby':


			if resetTimerstart > 0:
				global resetTimerend
				global resetTimer
				resetTimerend = time.time()
				resetTimer = resetTimerend - resetTimerstart
				print resetTimer
			
				if resetTimer > 10:
					reset()
			
		

