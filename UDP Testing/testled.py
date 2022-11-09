
import led
import time

counter = 0
while counter < 7:
    led.on(17, 4, 21, 26)
    time.sleep(0.1)
    led.off(17, 4, 21, 26)
    time.sleep(0.1)
    counter+=1 