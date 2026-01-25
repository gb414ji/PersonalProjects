import machine, time, network, urequests, gc

# --- CONFIG ---
WIFI_SSID = "₹ange"
WIFI_PASS = "Happy_890a"
TIME_URL = "http://worldtimeapi.org/api/timezone/Asia/Kolkata"

# --- HARDWARE ---
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
            self.write_cmd(cmd)
            if data is not None: self.write_data(data)
            if delay: time.sleep_ms(delay)
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A); self.write_data(bytearray([0, x0, 0, x1]))
        self.write_cmd(0x2B); self.write_data(bytearray([0, y0, 0, y1]))
        self.write_cmd(0x2C)
    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0: return
        self.set_window(x, y, x + w - 1, y + h - 1)
        chunk = bytearray([color >> 8, color & 0xFF] * w)
        for _ in range(h): self.write_data(chunk)
    def draw_char(self, x, y, char, color, size=1):
        font = {
            '0':[0x3E,0x51,0x49,0x45,0x3E],'1':[0x00,0x42,0x7F,0x40,0x00],'2':[0x42,0x61,0x51,0x49,0x46],'3':[0x21,0x41,0x45,0x4B,0x31],
            '4':[0x18,0x14,0x12,0x7F,0x10],'5':[0x27,0x45,0x45,0x45,0x39],'6':[0x3C,0x4A,0x49,0x49,0x30],'7':[0x01,0x71,0x09,0x05,0x03],
            '8':[0x36,0x49,0x49,0x49,0x36],'9':[0x06,0x49,0x49,0x29,0x1E],':':[0x00,0x36,0x36,0x00,0x00],' ':[0x00,0x00,0x00,0x00,0x00],
            '.':[0x00,0x60,0x60,0x00,0x00],'-':[0x00,0x08,0x08,0x08,0x00],'L':[0x7F,0x40,0x40,0x40,0x40],'O':[0x3E,0x41,0x41,0x41,0x3E],
            'A':[0x7C,0x12,0x11,0x12,0x7C],'D':[0x7F,0x41,0x41,0x22,0x1C],'I':[0x00,0x41,0x7F,0x41,0x00],'N':[0x7F,0x04,0x08,0x10,0x7F],
            'G':[0x3E,0x41,0x49,0x49,0x3A],'W':[0x7F,0x20,0x18,0x20,0x7F],'F':[0x7F,0x09,0x09,0x09,0x01],'P':[0x7F,0x09,0x09,0x09,0x06],
            'M':[0x7F,0x02,0x0C,0x02,0x7F],'S':[0x26,0x49,0x49,0x49,0x32],'U':[0x3F,0x40,0x40,0x40,0x3F],'T':[0x01,0x01,0x7F,0x01,0x01],
            'R':[0x7F,0x09,0x19,0x29,0x46],'E':[0x7F,0x49,0x49,0x49,0x41],'H':[0x7F,0x08,0x08,0x08,0x7F],'Y':[0x03,0x04,0x78,0x04,0x03],
            'X':[0x63,0x14,0x08,0x14,0x63]
        }
        bitmap = font.get(char, font[' '])
        for col in range(5):
            line = bitmap[col]
            for row in range(8):
                if (line >> row) & 1: self.fill_rect(x+col*size, y+row*size, size, size, color)

tft = CleanDisplay()

def animate_bar(text, duration_ms=1000):
    # Centered Text
    tft.fill_rect(0, 45, 160, 10, 0x0000)
    x_text = 80 - (len(text)*7 // 2)
    for c in text:
        tft.draw_char(x_text, 45, c, 0x07E0, size=1)
        x_text += 8
    
    # Progress Bar Frame (Static)
    tft.fill_rect(30, 65, 100, 10, 0xFFFF) # White Border
    tft.fill_rect(32, 67, 96, 6, 0x0000)   # Black Inside
    
    # Animated Fill
    steps = 20
    for i in range(steps + 1):
        w = int((i / steps) * 96)
        tft.fill_rect(32, 67, w, 6, 0x07E0) # Green Fill
        time.sleep_ms(duration_ms // steps)

def sync_time_persistent():
    wlan = network.WLAN(network.STA_IF)
    while not wlan.isconnected():
        animate_bar("ATRALIX", 800)
        wlan.active(False); time.sleep_ms(100); wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASS)
        # Quick check loop
        for _ in range(5):
            if wlan.isconnected(): break
            time.sleep_ms(500)
    
    synced = False
    while not synced:
        animate_bar("LOADING", 800)
        try:
            r = urequests.get(TIME_URL, timeout=5)
            j = r.json()
            dt = j['datetime']
            y, m, d = int(dt[0:4]), int(dt[5:7]), int(dt[8:10])
            hr, mn, sc = int(dt[11:13]), int(dt[14:16]), int(dt[17:19])
            machine.RTC().datetime((y, m, d, j['day_of_week'], hr, mn, sc, 0))
            r.close(); synced = True
        except:
            gc.collect()

def run():
    tft.fill_rect(0, 0, 160, 128, 0x0000)
    sync_time_persistent()
    tft.fill_rect(0, 0, 160, 128, 0x0000)
    
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    last_sec = -1
    
    while True:
        try:
            lt = time.localtime()
            if lt[5] != last_sec:
                # 1. Header
                x_in = 60
                for c in "INDIA": tft.draw_char(x_in, 5, c, 0xFBE0, size=1); x_in += 8

                # 2. Date & Day
                day_name = days[lt[6]] 
                date_str = "{:02d}-{:02d} {}".format(lt[2], lt[1], day_name)
                dx = 15
                for c in date_str:
                    tft.fill_rect(dx, 22, 12, 16, 0x0000)
                    tft.draw_char(dx, 22, c, 0x07FF, size=2); dx += 14

                # 3. Time 12H
                h24, m, s = lt[3], lt[4], lt[5]
                ampm = "AM" if h24 < 12 else "PM"
                h12 = h24 % 12 or 12
                time_str = "{:02d}:{:02d}:{:02d}".format(h12, m, s)
                tx = 25
                for char in time_str:
                    tft.fill_rect(tx, 52, 12, 16, 0x0000)
                    tft.draw_char(tx, 52, char, 0xFFFF, size=2); tx += 14 
                
                # 4. AM/PM
                tft.fill_rect(65, 80, 30, 10, 0x0000)
                tft.draw_char(65, 80, ampm[0], 0xF81F, size=1)
                tft.draw_char(73, 80, ampm[1], 0xF81F, size=1)

                # 5. Continuous Seconds Bar
                bar_width = int((s / 59) * 140)
                tft.fill_rect(10, 105, 140, 4, 0x3186) 
                tft.fill_rect(10, 105, bar_width, 4, 0x07E0) 

                last_sec = s
            time.sleep(0.1)
            gc.collect()
        except: machine.reset()

try: run()
except: machine.reset()
