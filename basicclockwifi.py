import machine
import time
import network
import urequests
import gc

# --- CONFIG ---
WIFI_SSID = "SSID"
WIFI_PASS = "Password"
TIME_URL = "http://worldtimeapi.org/api/timezone/Asia/Kolkata"

# --- HARDWARE CONFIG ---
SCK, MOSI, A0, RST, CS = 4, 5, 0, 1, 7
spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0, sck=machine.Pin(SCK), mosi=machine.Pin(MOSI))
a0, rst, cs = machine.Pin(A0, machine.Pin.OUT), machine.Pin(RST, machine.Pin.OUT), machine.Pin(CS, machine.Pin.OUT)

class CleanDisplay:
    def __init__(self):
        self.reset()
        self.init_tft()
    def write_cmd(self, cmd):
        a0.value(0); cs.value(0); spi.write(bytearray([cmd])); cs.value(1)
    def write_data(self, data):
        a0.value(1); cs.value(0); spi.write(data if isinstance(data, bytearray) else bytearray([data])); cs.value(1)
    def reset(self):
        rst.value(1); time.sleep_ms(10); rst.value(0); time.sleep_ms(100); rst.value(1); time.sleep_ms(100)
    def init_tft(self):
        for cmd, data, delay in [(0x01, None, 120), (0x11, None, 120), (0x3A, 0x05, 0), (0x36, 0x60, 0), (0x29, None, 100)]:
            self.write_cmd(cmd); 
            if data is not None: self.write_data(data)
            if delay: time.sleep_ms(delay)
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A); self.write_data(bytearray([0, x0, 0, x1]))
        self.write_cmd(0x2B); self.write_data(bytearray([0, y0, 0, y1]))
        self.write_cmd(0x2C)
    def fill_rect(self, x, y, w, h, color):
        self.set_window(x, y, x + w - 1, y + h - 1)
        chunk = bytearray([color >> 8, color & 0xFF] * w)
        for _ in range(h): self.write_data(chunk)
    def draw_char(self, x, y, char, color, size=1):
        font = {'0':[0x3E,0x51,0x49,0x45,0x3E],'1':[0x00,0x42,0x7F,0x40,0x00],'2':[0x42,0x61,0x51,0x49,0x46],'3':[0x21,0x41,0x45,0x4B,0x31],'4':[0x18,0x14,0x12,0x7F,0x10],'5':[0x27,0x45,0x45,0x45,0x39],'6':[0x3C,0x4A,0x49,0x49,0x30],'7':[0x01,0x71,0x09,0x05,0x03],'8':[0x36,0x49,0x49,0x49,0x36],'9':[0x06,0x49,0x49,0x29,0x1E],':':[0x00,0x36,0x36,0x00,0x00],' ':[0x00,0x00,0x00,0x00,0x00],'.':[0x00,0x60,0x60,0x00,0x00],'L':[0x7F,0x40,0x40,0x40,0x40],'O':[0x3E,0x41,0x41,0x41,0x3E],'A':[0x7C,0x12,0x11,0x12,0x7C],'D':[0x7F,0x41,0x41,0x22,0x1C],'I':[0x00,0x41,0x7F,0x41,0x00],'N':[0x7F,0x04,0x08,0x10,0x7F],'G':[0x3E,0x41,0x49,0x49,0x3A]}
        bitmap = font.get(char, font[' '])
        for col in range(5):
            line = bitmap[col]
            for row in range(8):
                if (line >> row) & 1: self.fill_rect(x+col*size, y+row*size, size, size, color)

tft = CleanDisplay()

def show_status_text(text, step=0):
    # This clears a wide area and draws the word + dots
    tft.fill_rect(20, 60, 120, 20, 0x0000)
    dots = "." * (step % 4)
    display_text = text + dots
    x_pos = 35
    for c in display_text:
        tft.draw_char(x_pos, 60, c, 0x07E0, size=1)
        x_pos += 8

def sync_time_persistent():
    wlan = network.WLAN(network.STA_IF)
    load_step = 0
    
    # WiFi Connection Loop
    while not wlan.isconnected():
        show_status_text("WIFI", load_step)
        load_step += 1
        wlan.active(False); time.sleep_ms(200); wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(10):
            if wlan.isconnected(): break
            time.sleep(1)

    # API Sync Loop
    synced = False
    while not synced:
        show_status_text("LOADING", load_step)
        load_step += 1
        try:
            r = urequests.get(TIME_URL, timeout=10, headers={'User-Agent': 'ESP32-Wu'})
            dt = r.json()['datetime']
            y, m, d = int(dt[0:4]), int(dt[5:7]), int(dt[8:10])
            hr, mn, sc = int(dt[11:13]), int(dt[14:16]), int(dt[17:19])
            machine.RTC().datetime((y, m, d, 0, hr, mn, sc, 0))
            r.close()
            synced = True
        except Exception as e:
            print("Sync Error:", e)
            gc.collect()
            time.sleep(2)

def run():
    tft.fill_rect(0, 0, 160, 128, 0x0000)
    sync_time_persistent()
    
    # Final Clock Face
    tft.fill_rect(0, 0, 160, 128, 0x0000)
    last_sec = -1
    while True:
        try:
            lt = time.localtime()
            if lt[5] != last_sec:
                time_str = "{:02d}:{:02d}:{:02d}".format(lt[3], lt[4], lt[5])
                curr_x = 30 
                for char in time_str:
                    tft.fill_rect(curr_x, 55, 12, 16, 0x0000)
                    tft.draw_char(curr_x, 55, char, 0xFFFF, size=2)
                    curr_x += 14 
                last_sec = lt[5]
            time.sleep(0.1)
            gc.collect()
        except:
            machine.reset()

try:
    run()
except:
    machine.reset()


