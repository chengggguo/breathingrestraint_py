import socket 
from time import sleep
from timeout import timeout
import RPi.GPIO as  GPIO

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


GPIO.setmode(GPIO.BCM)
 
#This the remote IP address to send the data too
HOST = '192.168.0.145'          
#This is the port the remove server is listening on
PORT = 10002               

#number of packets,will be replaced by data from sensor

capacity = 300
packetState = []
runingState = 'udp'
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


#init to reset all data and settings
def init():
	for i in range(capacity):
		packetState.append(True)

	#udpState = 'received'
	print 'init2 done'
	

def sendPackets():
	for i in range(capacity):
		if packetState[i] == True:
			packetState[i] = False
			message = str(i)
			# Send data to the server.
			s.sendto(message, (HOST, PORT))
	global udpState 
	udpState = 'sent'
	print udpState,'def sendPackets()'
		
		
@timeout(3)
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
	runningState = 'lisening'
 

def main():
	if udpState == 'received':
		sendPackets()
		print 'sent from main()'
		print udpState ,'def main()'

	else:
		recvPackets()
		print 'got'

def stateCheck(channel):
	value = mcp.read_adc_difference(channel)
	print value

	if value > 360:
		udpState = 'received'
	elif value < 160:
		udpState = 'valve'
	else:
		udpState = 'standby'


if __name__ == "__main__":
	init()
	while True:
		
		stateCheck(0)
		
		if udpState == 'received':
			sendPackets()
			
		elif udpState == 'sent':
			try:
				recvPackets()
				

			except:
				print 'timeout lalala'
				udpState = 'valve'
				

		elif udpState == 'valve':
			valveInhaling()
			udpState = 'standby'

		else:
			sleep(5)
			udpState = 'received'
			print 'lisening'




    
    

