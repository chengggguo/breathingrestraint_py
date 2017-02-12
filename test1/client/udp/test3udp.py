import socket 
from time import sleep
import RPi.GPIO as GPIO
import select
from threading import Timer

GPIO.setmode(GPIO.BCM)

pinState = 4  # breathing state
pinLost = 23  #relay for lost packets

#GPIO.setup(pinState, GPIO.OUT)
#GPIO.setup(pinLost, GPIO.OUT)

 
#This the remote IP address to send the data too
HOST = 'localhost'          
#This is the port the remove server is listening on
PORT = 10002               

#number of packets,will be replaced by data from sensor

capacity = 300
packetState = []
udpState = 'received'

# Create the socket and connect to the remote server.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#This is the port number the TransPort listens for data on and 
#accepts any IP address
s.bind(('', 10001))

#3s timeout for recvPrackets
timeout = 10

#s.setblocking(0)


#init to reset all data and settings
def init():
	for i in range(capacity):
		packetState.append(True)

	#udpState = 'received'
	#print 'init2 done'
	

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
		
		

def recvPackets():
	print 'receiving'
	data, addr = s.recvfrom(60000)	
	#print "get" , data
	index = int(data)
	packetState[index] = True
	print packetState[index], data


def valveInhaling():
	for i in range(capacity):
		if packetState[1] == True:
			print 'realy should on'
			GPIO.output(pinLost, True)
			sleep(0.1)
		else:
			print 'relay should off'
			GPIO.output(pinLost, False)
			sleep(0.1)


def delayed(seconds):
	def decorator(f):
		def wrapper(*args, **kargs):
			t.Timer(seconds, f, args, kargs)
			t.start()
		return wrapper
	return decorator
	

def main():
	if udpState == 'received':
		sendPackets()
		print 'sent from main()'
		print udpState ,'def main()'

	else:
		#ready = select.select([s],[],[],timeout)
		#if ready[0]:
			#while True:

			recvPackets()
			print 'got'




#if __name__ == "__main__":

init()
	
if udpState == 'received':
        sendPackets()
        print 'sent from main()'
        print udpState ,'def main()'

else:
	@delayed(3)
        #ready = select.select([s],[],[],timeout)
        #if ready[0]:
	def recvPackets():
        	print 'receiving'
        	data, addr = s.recvfrom(60000)
        	#print "get" , data
        	index = int(data)
        	packetState[index] = True
        	print packetState[index], data

        while True:
                recvPackets()
                print 'got'

	#while True:
	#	print 'round start', udpState
	#	main()
	#	print 'round done', udpState
print 'im out'
	#vavleInhaling()
