# 🕵️‍♂️ ESP32-Sniff: Real-Time Mobile Network Monitor

A lightweight, high-performance web-based packet sniffer built for the ESP32. It provides a Wireshark-like interface directly on your mobile browser, allowing for Deep Packet Inspection (DPI) of incoming HTTP/TCP traffic without any external software.

## 🚀 Key Features

* **Wireshark-Styled UI:** A dark-mode, tech-focused interface with a "Matrix Green" aesthetic.
* **Deep Packet Inspection (DPI):** Tap any packet row to slide up a details panel containing the full raw HTTP header (User-Agent, Host, Cookies, etc.).
* **Live Streaming:** Background polling (AJAX/JSON) ensures traffic flows into the UI in real-time without page reloads.
* **Memory Efficient:** Automatic garbage collection (`gc.collect()`) and packet-buffer capping to prevent ESP32 crashes during high traffic.
* **Zero-Install:** Works on any modern mobile or desktop browser via the ESP32's local IP.

---

## 📸 Interface Preview

<img width="1319" height="711" alt="Screenshot 2026-01-01 at 7 27 04 PM" src="https://github.com/user-attachments/assets/01774b1e-da26-4d87-931c-d4529c6148a4" />

## 🔧 Technical Implementation

### How it works:

1. **The Core:** Uses MicroPython's `socket` library to listen on Port 80.
2. **The Capture:** When a connection is made, the script captures the raw byte-stream of the header.
3. **The API:** A dedicated `/traffic` endpoint serves the latest captured packet in JSON format.
4. **The UI:** JavaScript on the client-side decodes the Base64 data and populates the "Wireshark" table.

---


## 🛠 Setup & Installation

### 1. Requirements

* **ESP32** (NodeMCU-32 38-Pin).
* **MicroPython Firmware** (v1.20 or later recommended).
* **Thonny IDE** for deployment.

### 2. Configuration

Update the `main.py` with your 2.4GHz WiFi credentials:

```python
SSID = "Your_WiFi_Name"
PASSWORD = "Your_WiFi_Password"

```

### 3. Usage

* Run the script and note the IP address in the console.
* Access the IP in your browser.
* Open a second tab or a different device and navigate to the same IP to generate "packets" for the monitor.

---

## 📊 Packet Data Captured

* **Timestamp:** Local browser-synced time.
* **Source IP:** The origin of the request.
* **Protocol:** Currently optimized for TCP/HTTP.
* **Deep Data:** Complete raw header strings for forensic analysis.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Part of the 2026 "Strong System" Hardware Series.**

---


<img width="2638" height="1422" alt="image" src="https://github.com/user-attachments/assets/4d217851-ce11-4b18-acfb-1eed46a49fd4" />
