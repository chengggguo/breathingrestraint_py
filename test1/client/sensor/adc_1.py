from gpiozero import MCP3008
from time import sleep

pot = MCP3008(0)

while True:
	print(pot.value)
	sleep(0.1)

