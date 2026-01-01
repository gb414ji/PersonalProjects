import network
import socket
import machine
import time
import gc
import json

# --- 1. CONFIGURATION ---
SSID = "YOUR_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
    ip = wlan.ifconfig()[0]
    print("\nConnected! IP:", ip)
    return ip

ip_addr = connect_wifi()

# --- 2. ADVANCED UI (WITH INSPECTOR) ---
html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <style>
        :root { --bg: #050505; --accent: #00ff41; --row: #0f0f0f; --text: #00ff41; --dim: #004411; --info: #00ccff; }
        body { font-family: 'Courier New', monospace; background: var(--bg); color: var(--text); margin: 0; padding: 10px; overflow: hidden; }
        
        .toolbar { display: flex; justify-content: space-between; font-size: 10px; border-bottom: 1px solid var(--dim); padding: 5px; margin-bottom: 5px; }
        .live-tag { color: #ff0000; animation: blink 1s infinite; font-weight: bold; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

        /* Packet List */
        .table-wrapper { height: 85vh; overflow-y: scroll; border: 1px solid var(--dim); }
        table { width: 100%; border-collapse: collapse; font-size: 11px; cursor: pointer; }
        th { position: sticky; top: 0; background: #1a1a1a; text-align: left; padding: 8px; border-bottom: 1px solid var(--dim); color: #fff; }
        td { padding: 10px 8px; border-bottom: 1px solid #111; white-space: nowrap; }
        tr:nth-child(even) { background: var(--row); }
        tr:active { background: var(--dim); }
        
        /* Inspector Overlay */
        #inspector { display:none; position: fixed; bottom: 0; left: 0; right: 0; height: 50vh; 
                      background: #000; border-top: 2px solid var(--accent); padding: 15px; 
                      overflow-y: auto; z-index: 100; box-shadow: 0 -10px 30px rgba(0,0,0,0.8); }
        .inspect-hdr { display: flex; justify-content: space-between; color: var(--accent); margin-bottom: 10px; font-weight: bold; }
        .full-data { color: var(--info); white-space: pre-wrap; word-break: break-all; font-size: 10px; }
        .close-btn { background: var(--accent); color: #000; border: none; padding: 2px 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="toolbar">
        <div><span class="live-tag">●</span> CAPTURING: wlan0</div>
        <div>IP: """ + ip_addr + """</div>
    </div>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr><th>TIME</th><th>SOURCE</th><th>INFO</th></tr>
            </thead>
            <tbody id="packets"></tbody>
        </table>
    </div>

    <div id="inspector">
        <div class="inspect-hdr">
            <span>PACKET DETAILS</span>
            <button class="close-btn" onclick="closeInspector()">X</button>
        </div>
        <div class="full-data" id="inspect-content"></div>
    </div>

    <script>
        function openInspector(fullContent) {
            document.getElementById('inspect-content').innerText = atob(fullContent);
            document.getElementById('inspector').style.display = 'block';
        }

        function closeInspector() {
            document.getElementById('inspector').style.display = 'none';
        }

        function addPacket(data) {
            if (!data.new) return;
            const tbody = document.getElementById('packets');
            const row = tbody.insertRow(0);
            const time = new Date().toLocaleTimeString('en-GB', {hour12:false});
            
            // Encode content to handle special characters in JS call
            const encodedContent = btoa(data.full);
            
            row.onclick = () => openInspector(encodedContent);
            row.innerHTML = `
                <td>${time}</td>
                <td style="color:#aaa">${data.ip}</td>
                <td style="color:var(--info)">${data.req}</td>
            `;
            
            if (tbody.rows.length > 30) tbody.deleteRow(30);
        }

        setInterval(() => {
            fetch('/traffic').then(r => r.json()).then(addPacket).catch(e => {});
        }, 1200);
    </script>
</body>
</html>
"""

# --- 3. SNIFFER LOGIC ---
last_packet = {"new": False, "ip": "0.0.0.0", "req": "", "full": ""}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

print("Deep Monitor Live at http://" + ip_addr)

while True:
    try:
        gc.collect()
        conn, addr = s.accept()
        conn.settimeout(0.5)
        try:
            raw_request = conn.recv(1024).decode()
        except:
            raw_request = ""

        if '/traffic' in raw_request:
            conn.send('HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(last_packet))
            last_packet["new"] = False 
        else:
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html)
            
            if raw_request:
                # Capture the first line for the table, and the whole block for the inspector
                lines = raw_request.split('\n')
                first_line = lines[0] if lines else "UNKNOWN"
                last_packet = {
                    "new": True,
                    "ip": str(addr[0]),
                    "req": first_line[:25] + "...",
                    "full": raw_request # This is the "Deep" data
                }
        
        conn.close()
    except Exception as e:
        print("Sniffer Error:", e)
