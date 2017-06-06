import time
from time import sleep

import socket
from timeout import timeout #timer
import RPi.GPIO as  GPIO

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

#for sensor via mcp3008
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

GPIO.setmode(GPIO.BCM)

#This the remote IP address to send the data too
HOST = '192.168.0.145'
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
capacity = 0
duration = 0
tStart = 0
tEnd =0
init = True # should start from inhale
capacity = 0
packetState = []
udpState = 'standby'
unit = 600 #inhaling unit, will use it to divide the total capacity, it controls the inhaling length/running time
unitRounds = 0 #number of inhaling rounds per one data flow 
unitCounter = 0 

n = 0

#init to reset all data and settings
def init():
	pass

@timeout(3) # 3seconds timer
def sendPackets():
        for i in range(capacity):
                if packetState[i] == True:
                        packetState[i] = False
                        message = str(i)
                        # Send data to the server.
                        s.sendto(message, (HOST, PORT))
        global udpState
        udpState = 'sent'
	global unitCounter
	global n
	unitCounter = 0
	n = 0
        print udpState,'def sendPackets()'
        while True:
                data, addr = s.recvfrom(60000)
                #print "get" , data
                index = int(data)
                packetState[index] = True
                print packetState[index], data


def recvPackets():#could be deleted later
        while True:
                data, addr = s.recvfrom(60000)
                #print "get" , data
                index = int(data)
                packetState[index] = True
                print packetState[index], data

def valveInhaling():
	global n
	global unitCounter
	global inhaled
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

def checkState():
	global state
	global stateCheck
	global tStart
	global inhaled
	value = mcp.read_adc_difference(0)
	if value > 800:
                state = 'blow'
		stateCheck = False
		inhaled = False
		print 'stateCheck >650' ,value
	elif value < 600:
                state = 'inhale'
                stateCheck = False
                print 'stateCheck <600', value
                maxV = value
                tStart = time.time()
	else:
                state = 'standby'
                print 'listening',value
		stateCheck = True
                               

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
			if inhaled:
				checkState()
			else:
				if init:
					print 'inhaling'
					sleep(0.05)
                        	        if maxV < value:
                                	        maxV = value
						print 'get maxspeed: ', maxV
	                                if value > 600:
        	                                print 'inhale end'
						global tEnd
                	                        tEnd = time.time()
						global duration
                        	                duration = tEnd - tStart
						global capacity
						print 'maxspeed: ', maxV,'started at: ', tStart, 'ended at: ', tEnd, 'duration: ' , duration
	                                        sleep(1)###############################################
						capacity = int(duration * maxV)
	                                        print 'capacity' , capacity
						sleep(1)###################### delet later
						global unitRounds
						unitRounds = capacity/unit
						print 'will inhale', unitRounds, 'rounds'
						sleep(5) ################################# will be deleted
                	                        stateCheck = True
						if capacity <100:
							pass
						else:
							init = False
							for i in range(capacity):
				               			 packetState.append(True)
							udpState = 'ready'
						global inhaled
						inhaled = True


				else:
					valveInhaling()

			
		elif state == 'blow':
			print 'blow',value
			if udpState == 'sent':
				
				if value <700:
					stateCheck = True
			else:
				if init:
					if value < 800:
						stateCheck = True
				
				else:
					try:
						sendPackets()
					except:
						print 'recvtimeoooooooooooout'
						checkState()
						

		elif state == 'standby':
			pass




			
		

