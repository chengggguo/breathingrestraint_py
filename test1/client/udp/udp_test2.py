import socket 
from time import sleep
 
#This the remote IP address to send the data too
HOST = 'localhost'          
#This is the port the remove server is listening on
PORT = 10002               

#number of packets,will be replaced by data from sensor

capacity = 1000
packetState = []


#init to reset all data and settings
def init():
	for i in range(capacity):
		packetState.append(True)
	

def sendPackets():
	# Create the socket and connect to the remote server.
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#This is the port number the TransPort listens for data on and 
	#accepts any IP address
	s.bind(('', 10001))
 
	for i in range(capacity):
		if packetState[i] == True:
			packetState[i] = False
			
			message = str(i)
			# Send data to the server.
			s.sendto(message, (HOST, PORT))
		
		
		
	for i in range(capacity):
		data, addr = s.recvfrom(60000)	
		#print "get" , data
		index = int(data)
		packetState[index] = True
		print packetState[i]
		if packetState[i] == True:
			print "yes"
		
	#for i in range(capacity):
	#	if packetState[i] == True:
	#		print 'yes'
	#	if packetState[i] == False:
	#		print 'no'

	#sleep(1)
	#s.close()
 

def main():
	#init()
	sendPackets()

while True:

	init()
	main()

	#sleep(10)
