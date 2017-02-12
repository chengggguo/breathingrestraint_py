import socket 
from time import sleep
from timeout import timeout
 
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


 

def main():
	if udpState == 'received':
		sendPackets()
		print 'sent from main()'
		print udpState ,'def main()'

	else:
		recvPackets()
		print 'got'



if __name__ == "__main__":
	init()
	while True:
		if udpState == 'received':
			sendPackets()
			print udpState ,'def main()'

		elif udpState == 'sent':		
			try:
				recvPackets()
				print 'got'

			except:
				udpState = 'roundDone'

		elif udpState == 'roundDone':
			print 'listening'




    
    

