import serial
import struct
import time
from timeout import timeout
import threading

try:
	ser = serial.Serial("/dev/ttyACM0",9600)
	time.sleep(2) # it needs a delay for the serial connection
except:
	ser = serial.Serial("/dev/ttyACM1",9600)
	time.sleep(2)

fh=open("number.txt","r")
num = fh.readline()
fh.close() 
print num
#num = '1356'
time.sleep(1)


def init():
	fh = open("number.txt","w")
        fh.truncate()
        fh.write(num)
        fh.close()
	
t = threading.Timer(3.0,init)

def sendNumLed():
	reversedNum = num[::-1] #reverse the string of number
	if 16-len(reversedNum) > 0:
		for i in range(16-len(reversedNum)):
			reversedNum = reversedNum + '0'
	for i in range(len(reversedNum)): # send digits to the led one by one
		ser.write(struct.pack('>B',int(reversedNum[i])))


if  True:
	t.start()
	while True:
		sendNumLed()
		num=str(int(num)+1)
		time.sleep(1)
