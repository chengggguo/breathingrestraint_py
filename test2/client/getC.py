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
HOST = 'localhost'
#This is the port the remove server is listening on
PORT = 10002

#number of packets,will be replaced by data from sensor

capacity = 0
packetState = []
udpState = 'received'

# Create the socket and connect to the remote server.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#This is the port number the TransPort listens for data on and 
#accepts any IP address
s.bind(('', 10001))


pinState = 4
pinInhale = 23

ledState = 26
ledInhale = 13

#relaies for controlling valves
GPIO.setup(pinState,GPIO.OUT)  #breathing state
GPIO.setup(pinInhale,GPIO.OUT) #relay for lost packets
GPIO.setup(ledState, GPIO.OUT)
GPIO.setup(ledInhale,GPIO.OUT)


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
maxV = 0
capacity = 0
duration = 0
tStart = 0
tEnd =0
init = True # should start from inhale

#init to reset all data and settings
def init():
	pass

@timeout(2)
def sendPackets():
        for i in range(capacity):
                if packetState[i] == True:
                        packetState[i] = False
                        message = str(i)
                        # Send data to the server.
                        s.sendto(message, (HOST, PORT))
#        global udpState
#        udpState = 'sent'
        print udpState,'def sendPackets()'
        while True:
                data, addr = s.recvfrom(60000)
                #print "get" , data
                index = int(data)
                packetState[index] = True
                print packetState[index], data


def recvPackets():
        while True:
                data, addr = s.recvfrom(60000)
                #print "get" , data
                index = int(data)
                packetState[index] = True
                print packetState[index], data

def valveInhaling():
        for i in range(capacity):
                if packetState[i] == True:
                        GPIO.output(pinInhale,True)
                        GPIO.output(ledInhale,True)
                        print packetState[i]
                        sleep(0.05)
                else:
                        GPIO.output(pinInhale,False)
                        GPIO.output(ledInhale,False)
                        print packetState[i]
                        sleep(0.05)
        state = 'standby'
	stateCheck = True
#	udpState = 'received'
#	init = False


if __name__ == "__main__":
	while True:
		value = mcp.read_adc_difference(0)
		#sleep(0.1)
		if stateCheck:
        		#print value
        		if value > 650:
                		state = 'blow'
                		stateCheck = False
                		print 'stateCheck >650' ,value
        		elif value < 600:
                		state = 'inhale'
                		stateCheck = False
                		print 'stateCheck <600', value

                		maxV = value
                		#global tStart
                		tStart = time.time() 
			else:
				state = 'standby'
	                	print 'listening',value
	
		if state == 'inhale':
			print value 

			if init:
				print 'inhaling'
				sleep(0.05)
                                if maxV > value:
                                        maxV = value
                                if value > 600:
                                        print 'inhale end '
                                        #global tEnd
                                        tEnd = time.time()
                                        duration = tEnd - tStart
					global capacity
                                        capacity = int(duration * maxV)
                                        print 'capacity' , capacity
                                        udpState = 'received'
                                        sleep(1)
                                        stateCheck = True
					init = False
					for i in range(capacity):
				                packetState.append(True)


			else:
				valveInhaling()
				print 'udpstate = valve'

			
		elif state == 'blow':
			print 'blow',value
			if init:
				if value < 650:
					stateCheck = True
				
			else:
				try:
					sendPackets()
				except:
					stateCheck = True
					print 'recvtimeoooooooooooout'

		elif state == 'standby':
			pass		




			
		

