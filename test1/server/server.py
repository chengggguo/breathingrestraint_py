import socket
import sys

# Create a TCP/IP Server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10002)
print >>sys.stderr, 'starting up on %s port %s' % server_address

sock.bind(server_address)

n = 0

while True:
	print sys.stderr, 'saiting to receive message'
	data, address = sock.recvfrom(60000)

	#print sys.stderr, 'received %s bytes from %s' % (len(data),address)
	print sys.stderr, data

	if data:
		sock.sendto(data, address)
		n = n + 1

		#print n
