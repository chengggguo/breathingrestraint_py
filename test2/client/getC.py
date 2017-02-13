import time
from time import sleep

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


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

while True:

	value = mcp.read_adc_difference(0)
	sleep(0.01)
	if stateCheck:

		if value > 650:
			state = 'blow'
			stateCheck = False
			maxV = value
			#global tStart
			tStart = time.time()
      			print 'stateCheck >170' ,value
		elif value < 600:
			state = 'inhale'
			stateCheck = False
			print 'stateCheck <160', value
		else:
			state = 'standby'
			print 'listening',value
	
	if state == 'inhale':
		print 'inhaling'
		if maxV < value:
			print 'inhale start'
			maxV = value
		if value > 600:
			print 'inhale end '
			#global tEnd
			tEnd = time.time()
			duration = tEnd - tStart
			capacity = int(duration * maxV)
			print capacity
			sleep(10)
			stateCheck = True
			
	if state == 'blow':
		print 'blow',value
		if value < 650:
			stateCheck = True


			
		

