import machine
import time

# --- HARDWARE CONFIG ---
SCK, MOSI, A0, RST, CS = 4, 5, 0, 1, 7
spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0, sck=machine.Pin(SCK), mosi=machine.Pin(MOSI))
a0, rst, cs = machine.Pin(A0, machine.Pin.OUT), machine.Pin(RST, machine.Pin.OUT), machine.Pin(CS, machine.Pin.OUT)

class CleanDisplay:
    def __init__(self):
        self.reset()
        self.init_tft()
        
    def write_cmd(self, cmd):
        a0.value(0); cs.value(0)
        spi.write(bytearray([cmd]))
        cs.value(1)

    def write_data(self, data):
        a0.value(1); cs.value(0)
        spi.write(data if isinstance(data, bytearray) else bytearray([data]))
        cs.value(1)

    def reset(self):
        rst.value(1); time.sleep_ms(10); rst.value(0); time.sleep_ms(100); rst.value(1); time.sleep_ms(100)

    def init_tft(self):
        # 0x36, 0x60 = Landscape
        # I removed the 0x21 (Inversion) command to fix your black/white swap
        for cmd, data, delay in [
            (0x01, None, 120), (0x11, None, 120), (0x3A, 0x05, 0), 
            (0x36, 0x60, 0), (0x29, None, 100)
        ]:
            self.write_cmd(cmd)
            if data is not None: self.write_data(data)
            if delay: time.sleep_ms(delay)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A); self.write_data(bytearray([0, x0, 0, x1]))
        self.write_cmd(0x2B); self.write_data(bytearray([0, y0, 0, y1]))
        self.write_cmd(0x2C)

    def fill_rect(self, x, y, w, h, color):
        if x < 0 or y < 0 or x+w > 160 or y+h > 128: return
        self.set_window(x, y, x + w - 1, y + h - 1)
        chunk = bytearray([color >> 8, color & 0xFF] * w)
        for _ in range(h): self.write_data(chunk)

    def draw_char(self, x, y, char, color, size=2):
        font = {
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E], '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
            '2': [0x42, 0x61, 0x51, 0x49, 0x46], '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
            '4': [0x18, 0x14, 0x12, 0x7F, 0x10], '5': [0x27, 0x45, 0x45, 0x45, 0x39],
            '6': [0x3C, 0x4A, 0x49, 0x49, 0x30], '7': [0x01, 0x71, 0x09, 0x05, 0x03],
            '8': [0x36, 0x49, 0x49, 0x49, 0x36], '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
            ':': [0x00, 0x36, 0x36, 0x00, 0x00], ' ': [0x00, 0x00, 0x00, 0x00, 0x00]
        }
        bitmap = font.get(char, font[' '])
        for col in range(5):
            line = bitmap[col]
            for row in range(8):
                if (line >> row) & 1:
                    self.fill_rect(x + col*size, y + row*size, size, size, color)

# --- RUN LOOP ---
tft = CleanDisplay()
tft.fill_rect(0, 0, 160, 128, 0x0000) # Should be Deep Black now

def run():
    print("UI Flipped: White text on Black background.")
    last_sec = -1
    
    while True:
        lt = time.localtime()
        if lt[5] != last_sec:
            time_str = "{:02d}:{:02d}:{:02d}".format(lt[3], lt[4], lt[5])
            
            curr_x = 30 
            for char in time_str:
                # Clear with 0x0000 (Black)
                tft.fill_rect(curr_x, 55, 12, 16, 0x0000)
                # Draw with 0xFFFF (White)
                tft.draw_char(curr_x, 55, char, 0xFFFF, size=2)
                curr_x += 14 
            
            last_sec = lt[5]
        time.sleep(0.1)

try:
    run()
except Exception as e:
    print("Error:", e)
