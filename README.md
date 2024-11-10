# Sprig-Spear
![Sprig Dino Spear Edition](https://raw.githubusercontent.com/m5kro/Sprig-Spear/main/SPRIGDINO-Spear-Edition.png) <br>
Spear is a custom firmware built using micropython for the Hack Club Sprig console used for cybersecurity pentesting. Scroll down for instructions.
# Credits
Hack Club team for the [Sprig](https://github.com/hackclub/sprig/) :D <br>
ECTO-1A for the [AppleJuice](https://github.com/ECTO-1A/AppleJuice) Code
# Current Features
1. Bluetooth AppleJuice Attack (Read Disclaimer)
2. USB Keyboard
3. Read rubber ducky payloads (not all functions supported)
# Upcoming Features (No particular order)
1. WiFi Deauth Attack (missing monitor mode)
2. WiFi Beacon Spam
3. WiFi Evil Twin
4. Bluetooth Deauth
5. Bluetooth L2CAP ping
6. Bluetooth Fake device (maybe)
7. Pn532 NFC addon (Very Unlikely)
8. Rewrite/Reorganize code
9. Read from microsd card slot
# Disclaimers
1. I'm not responsible for what you do so don't do anything stupid. (I know some of you will)
2. AppleJuice attack has been patched by Apple. The attack is also unreliable due to possible ETIMEOUT Error.
# Setup Instructions
1. Download [Micropython](https://micropython.org/download/RPI_PICO_W/)
2. Flash to the Pico W (Newer versions of the Sprig come with a Pico W)
3. Use [Thonny](https://thonny.org/) or [MicroPico](https://github.com/paulober/MicroPico) to send main.py, ST7735.py, and applejuice.py to the Pico W
4. Install mpremote using pip `python3 -m pip install mpremote`
5. Install keyboard libraries `python3 -m mpremote mip install usb-device-keyboard`, you may need to close vscode or thonny during this part
6. Put rubber ducky payloads at root as .ducky files
7. Reboot the Pico W
8. Use buttons to navigate. Up/Down to select, Right to enter, Left to go back
