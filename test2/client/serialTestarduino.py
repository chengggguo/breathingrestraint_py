import serial
import struct
import time


ser = serial.Serial("/dev/ttyACM1",9600)
time.sleep(2) # it needs a delay for the serial connection
fh=open("number.txt","r")
num = fh.readline()
print num
time.sleep(1)

def sendNumLed():
	reversedNum = num[::-1] #reverse the string of number
	if 16-len(reversedNum) > 0:
		for i in range(16-len(reversedNum)):
			reversedNum = reversedNum + '0'
	for i in range(len(reversedNum)): # send digits to the led one by one
		ser.write(struct.pack('>B',int(reversedNum[i])))


while True:
	sendNumLed()
	time.sleep(1)
