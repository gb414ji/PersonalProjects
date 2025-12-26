from machine import Pin, SPI
import max7219
import time

# SPI setup
spi = SPI(0, baudrate=10000000, polarity=0, phase=0,
          sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)

# Create display (1 matrix)
display = max7219.Matrix8x8(spi, cs, 1)
display.brightness(5)
display.fill(0)

# Smiley face frames
smile_open = [
    0b00111100,
    0b01000010,
    0b10100101,
    0b10000001,
    0b10100101,
    0b10011001,
    0b01000010,
    0b00111100
]

smile_wink = [
    0b00111100,
    0b01000010,
    0b10100001,
    0b10000001,
    0b10100101,
    0b10011001,
    0b01000010,
    0b00111100
]

def draw(frame):
    display.fill(0)
    for y in range(8):
        for x in range(8):
            if frame[y] & (1 << (7 - x)):
                display.pixel(x, y, 1)
    display.show()

# Animation loop
while True:
    draw(smile_open)
    time.sleep(1)

    draw(smile_wink)
    time.sleep(0.3)

    draw(smile_open)
    time.sleep(1)

