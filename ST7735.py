from machine import Pin, SPI
import os
import time
import sdcard

# ST7735 Commands
ST7735_SWRESET = 0x01
ST7735_SLPOUT  = 0x11
ST7735_FRMCTR1 = 0xB1
ST7735_FRMCTR2 = 0xB2
ST7735_FRMCTR3 = 0xB3
ST7735_INVCTR  = 0xB4
ST7735_PWCTR1  = 0xC0
ST7735_PWCTR2  = 0xC1
ST7735_PWCTR3  = 0xC2
ST7735_PWCTR4  = 0xC3
ST7735_PWCTR5  = 0xC4
ST7735_VMCTR1  = 0xC5
ST7735_INVOFF  = 0x20
ST7735_MADCTL  = 0x36
ST7735_COLMOD  = 0x3A
ST7735_CASET   = 0x2A
ST7735_RASET   = 0x2B
ST7735_RAMWR   = 0x2C
ST7735_GMCTRP1 = 0xE0
ST7735_GMCTRN1 = 0xE1
ST7735_DISPON  = 0x29
ST7735_NORON   = 0x13

# Color Definitions
BLACK = 0x0000
WHITE = 0xFFFF

# Pin Configuration for ST7735 Display
TFT_CS = Pin(20, Pin.OUT)
TFT_RST = Pin(26, Pin.OUT)
TFT_DC = Pin(22, Pin.OUT)

# Pin Configuration for SD Card
CARD_CS = Pin(21, Pin.OUT)

# SPI Setup for Display and SD Card (shared SPI bus)
spi = SPI(0, baudrate=30000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))

def write_command(cmd):
    TFT_DC.value(0)
    TFT_CS.value(0)
    spi.write(bytearray([cmd]))
    TFT_CS.value(1)

def write_data(data):
    TFT_DC.value(1)
    TFT_CS.value(0)
    spi.write(bytearray([data]))
    TFT_CS.value(1)

def init_display():
    TFT_RST.value(1)
    time.sleep(0.1)
    TFT_RST.value(0)
    time.sleep(0.1)
    TFT_RST.value(1)
    time.sleep(0.1)

    write_command(ST7735_SWRESET)
    time.sleep(0.15)
    write_command(ST7735_SLPOUT)
    time.sleep(0.5)

    write_command(ST7735_FRMCTR1)
    write_data(0x01)
    write_data(0x2C)
    write_data(0x2D)

    write_command(ST7735_FRMCTR2)
    write_data(0x01)
    write_data(0x2C)
    write_data(0x2D)

    write_command(ST7735_FRMCTR3)
    write_data(0x01); write_data(0x2C); write_data(0x2D)
    write_data(0x01); write_data(0x2C); write_data(0x2D)

    write_command(ST7735_INVCTR)
    write_data(0x07)

    write_command(ST7735_PWCTR1)
    write_data(0xA2)
    write_data(0x02)
    write_data(0x84)

    write_command(ST7735_PWCTR2)
    write_data(0xC5)

    write_command(ST7735_PWCTR3)
    write_data(0x0A)
    write_data(0x00)

    write_command(ST7735_PWCTR4)
    write_data(0x8A)
    write_data(0x2A)

    write_command(ST7735_PWCTR5)
    write_data(0x8A)
    write_data(0xEE)

    write_command(ST7735_VMCTR1)
    write_data(0x0E)

    write_command(ST7735_INVOFF)

    write_command(ST7735_MADCTL)
    write_data(0x60)  # Set to landscape mode

    write_command(ST7735_COLMOD)
    write_data(0x05)

    write_command(ST7735_CASET)
    write_data(0x00)
    write_data(0x00)
    write_data(0x00)
    write_data(0x9F)

    write_command(ST7735_RASET)
    write_data(0x00)
    write_data(0x00)
    write_data(0x00)
    write_data(0x7F)

    write_command(ST7735_GMCTRP1)
    write_data(0x02); write_data(0x1C); write_data(0x07); write_data(0x12)
    write_data(0x37); write_data(0x32); write_data(0x29); write_data(0x2D)
    write_data(0x29); write_data(0x25); write_data(0x2B); write_data(0x39)
    write_data(0x00); write_data(0x01); write_data(0x03); write_data(0x10)

    write_command(ST7735_GMCTRN1)
    write_data(0x03); write_data(0x1D); write_data(0x07); write_data(0x06)
    write_data(0x2E); write_data(0x2C); write_data(0x29); write_data(0x2D)
    write_data(0x2E); write_data(0x2E); write_data(0x37); write_data(0x3F)
    write_data(0x00); write_data(0x00); write_data(0x02); write_data(0x10)

    write_command(ST7735_NORON)
    time.sleep(0.01)

    write_command(ST7735_DISPON)
    time.sleep(0.1)

def update_display(fb):
    write_command(ST7735_CASET)
    write_data(0x00); write_data(0x00)
    write_data(0x00); write_data(0x9F)
    write_command(ST7735_RASET)
    write_data(0x00); write_data(0x00)
    write_data(0x00); write_data(0x7F)
    write_command(ST7735_RAMWR)
    TFT_DC.value(1)
    TFT_CS.value(0)
    spi.write(fb)
    TFT_CS.value(1)

# Attempt to mount SD card if available
def mount_sd():
    try:
        # Initialize SD card
        sd = sdcard.SDCard(spi, CARD_CS, baudrate=30000000)  # Initialize SD card on the same SPI bus at the same speed

        # Try to mount the SD card
        os.mount(sd, "/sd")
    except OSError:
        spi.init(baudrate=30000000, polarity=0, phase=0)
        # If SD card mount fails, fall back to internal storage
        print("SD card not accessible. Using internal storage.")