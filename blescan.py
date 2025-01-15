# Why was this so hard ... who designed BLE?
import sys
import gc
# Spent hours going in circles before I found aioble ;(
import aioble
import uasyncio as asyncio

# Helper to detect uasyncio v3
IS_UASYNCIO_V3 = hasattr(asyncio, "__version__") and asyncio.__version__ >= (3,)


class BLEScanner:
    def __init__(self):
        self.devices = []

    async def start_scan(self):
        # Can't use active scanning as it causes the pico to stall
        async with aioble.scan(duration_ms=5000) as scanner:
            async for result in scanner:
                device_info = {
                    "address": ':'.join(['%02X' % i for i in result.device.addr]),
                    "rssi": result.rssi,
                    "connectable": result.connectable,
                }
                self.devices.append(device_info)

    async def run(self):
        """Run the BLE scanner."""
        loop = asyncio.get_event_loop()
        if IS_UASYNCIO_V3:
            loop.set_exception_handler(self._handle_exception)

        try:
            await self.start_scan()
        except Exception as e:
            print(f"Error during scan: {e}")
            sys.print_exception(e)

    @staticmethod
    def _handle_exception(loop, context):
        """Global exception handler for uasyncio v3."""
        sys.print_exception(context["exception"])
        sys.exit()


# Entry point
def startup():
    try:
        scanner = BLEScanner()
        if IS_UASYNCIO_V3:
            asyncio.run(scanner.run())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(scanner.run())
        return scanner.devices
    except Exception as e:
        sys.print_exception(e)
        return []
    finally:
        if IS_UASYNCIO_V3:
            asyncio.new_event_loop()  # Clear retained state