from gpiozero import LED, Button
from time import sleep
from signal import pause

led1 = LED(10)
led2 = LED(24)
button = Button(17)
#button.when_pressed = led
#button.when_released = no_led
while True:
        if button.is_pressed:
                led1.on()
                sleep(1)
                led2.on()
                sleep(1)
                led1.off()
                sleep(1)
                led2.off()
                sleep(1)
        else: pass
