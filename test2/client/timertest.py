from time import sleep
import threading
from random import random

def timout():
	print "dddd"
	sleep(3)

t=threading.Timer(4.0,timout)
print 'got'
#t.start

if  True:
	t.start()
#if random()<0.1:
#	t.cancel()
#	print('canceling')


