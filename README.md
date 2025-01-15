# Sprig-Spear
![Sprig Dino Spear Edition](https://raw.githubusercontent.com/m5kro/Sprig-Spear/main/SPRIGDINO-Spear-Edition.png) <br>
Spear is a custom firmware built using micropython for the Hack Club Sprig console used for cybersecurity pentesting. Scroll down for instructions.<br>
<br>
Development for Spear has completed. Hack Club has decided to switch to the [Orpheus Pico](https://orpheuspico.hackclub.com/) as the microcontroller for the Sprig console. The Orpheus Pico does not have a WiFi/Bluetooth chipset and as such won't be able to perform the majority of Spear's functions.<br>
<br>
Thank you to everyone who used Spear! See you in the next project!
# Credits
Hack Club team for the [Sprig](https://github.com/hackclub/sprig/) :D <br>
ECTO-1A for the [AppleJuice](https://github.com/ECTO-1A/AppleJuice) Code <br>
Chris Hager for most of the [Captive Portal](https://github.com/metachris/micropython-captiveportal) Code
# Current Features
1. Bluetooth AppleJuice Attack (Read Disclaimer)
2. USB Keyboard
3. Read rubber ducky payloads (not all functions supported)
4. Read from microsd card slot
5. WiFi Evil Twin
6. WiFi Evil Twin customization (read disclaimer)
7. WiFi Beacon Spam
8. BLE Device Scanning and Info
# ~~Upcoming~~ Features That Will Never Be Implemented
1. WiFi Deauth Attack (missing monitor mode)
2. Bluetooth Deauth (bad Bluetooth classic support)
3. Bluetooth L2CAP ping
4. Bluetooth Fake device
# Disclaimers
1. I'm not responsible for what you do so don't do anything stupid. (I know some of you will)
2. AppleJuice attack has been patched by Apple. The attack is also unreliable due to possible ETIMEOUT Error.
3. Captive portal files can only go up to a certain size before the pico freaks out and hard resets.
4. Applejuice attacks may take up to 5 seconds to exit.
5. The BLE Scanning submenu can sometimes stall the pico due to memory overload 
# Setup Instructions
1. Download [Micropython](https://micropython.org/download/RPI_PICO_W/)
2. Flash to the Pico W (Newer versions of the Sprig come with a Pico W)
3. Use [Thonny](https://thonny.org/) or [MicroPico](https://github.com/paulober/MicroPico) to send all the python files to the Pico W
4. Install mpremote using pip `python3 -m pip install mpremote`
5. Install keyboard libraries `python3 -m mpremote mip install usb-device-keyboard`, you may need to close vscode or thonny during this part
6. Install aioable for BLE scanning `python3 -m mpremote mip install aioble-central`
7. Install sdcard libraries `python3 -m mpremote mip install sdcard`
8. Put rubber ducky payloads in a folder called ducks at root or on sdcard (fat32) as .ducky files
9. Put beacons.txt in root or on sdcard (contains SSID names for beacon spamming)
10. Follow instructions below for captive portals
11. Reboot the Pico W
12. Use buttons to navigate. Up/Down to select, Right to enter, Left to go back
13. You can find captured credentials in cred.txt at the root folder<br>
<br>
Note: You must create a ducks folder, a beacons.txt file, and a portals folder at root or else the device won't boot<br>
<br>
Optional: Place bootimg.raw at root to get a fun splash screen at boot<br>
# Captive Portal Instructions
1. Create a folder called portals in root or on sdcard
2. Inside portals create a folder with whatever name you want
3. Inside your created folder, make a file called config.txt
4. Place your SSID (WiFi name) and password inside config.txt <br>
Example (leave PASS blank for open network): <br>
```
SSID = "TEST"
PASS = ""
```
5. Create a file called index.html
6. Place your login page inside index.html, have it return username and password through POST requests <br>
Note: There is no support for images or reading other files as index.html can only reach a few kb in size <br>
Example:
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Page</title>
</head>
<body>
    <h1>Welcome to the Captive Portal</h1>
    <form action="/" method="POST">
        <label for="username">Username:</label>
        <br>
        <input type="text" id="username" name="username" required>
        <br><br>
        <label for="password">Password:</label>
        <br>
        <input type="password" id="password" name="password" required>
        <br><br>
        <button type="submit">Login</button>
    </form>
    </body>
</html>
```