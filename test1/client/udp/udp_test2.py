import socket, time
 
#This the remote IP address to send the data too
HOST = 'localhost'          
#This is the port the remove server is listening on
PORT = 10002               
 
 
def main():
    # Create the socket and connect to the remote server.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #This is the port number the TransPort listens for data on and 
    #accepts any IP address
    s.bind(('', 10001))
 
    message = "hello"
 
    # Send data to the server.
    s.sendto(message, (HOST, PORT))
    data, addr = s.recvfrom(60000)
    print "recevived", data
    #s.close()
 
if __name__ == '__main__':
    while True:
	time.sleep(0.1)
	main()
