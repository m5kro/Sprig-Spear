from machine import Pin, PWM, Timer
import time
import applejuice
import ST7735  # Import the display module
import framebuf
from keystrokes import interpret_ducky_script # For executing Rubber Ducky scripts
import os
import captivewifi

# Color Definitions
BLACK = ST7735.BLACK
WHITE = ST7735.WHITE

# Button Configuration
button_up = [Pin(12, Pin.IN, Pin.PULL_UP), Pin(5, Pin.IN, Pin.PULL_UP)]
button_down = [Pin(14, Pin.IN, Pin.PULL_UP), Pin(7, Pin.IN, Pin.PULL_UP)]
button_left = [Pin(13, Pin.IN, Pin.PULL_UP), Pin(6, Pin.IN, Pin.PULL_UP)]
button_right = [Pin(15, Pin.IN, Pin.PULL_UP), Pin(8, Pin.IN, Pin.PULL_UP)]

# Menu Configuration
main_menu = ["WiFi", "Bluetooth", "USB"]
wifi_submenu = ["Captive Portal"]
captive_portal_submenu = ["Test"]
bluetooth_submenu = ["AppleJuice"]
usb_submenu = ["Rubber Ducky"]
rubber_ducky_submenu = []  # This will be populated with .ducky files on startup
captive_portal_list = [] # This will be populated with captive portal options
payload_names = applejuice.payload_names

# State Variables
selected_index = 0
display_start_index = 0
max_display_items = 6  # Maximum number of items to display on screen
initial_y_position = 10  # Initial y position for the menu
current_menu = main_menu
previous_menu_stack = []
scroll_offset = 0
last_scroll_time = time.ticks_ms()  # To control scrolling speed
payload_selected_index = 0  # To save the selected payload index
interval_value = 200  # Initial interval value
loop_interval_value = 5  # Initial loop interval value

# Power Light Configuration
power_light_pin = 28
pwm_power_light = PWM(Pin(power_light_pin))
pwm_power_light.freq(1000)
pwm_power_light.duty_u16(65535 // 8)  # Dim the light

status_light_pin = 4
pwm_status_light = PWM(Pin(status_light_pin))
pwm_status_light.freq(1000)

def flash_status_light():
    pwm_status_light.duty_u16(65535 // 8)  # Turn on status light
    time.sleep(0.1)  # Keep it on for a fraction of a second
    pwm_status_light.duty_u16(0)  # Turn off the status light

# Load .ducky scripts from SD card or root directory at startup
def load_ducky_scripts():
    global rubber_ducky_submenu
    ducky_files = []

    # Try to list files from the SD card directory
    try:
        ducky_files = ["/sd/ducks/" + f[:-6] for f in os.listdir("/sd/ducks") if f.endswith('.ducky')]
        ducky_files += ["ducks/" + f[:-6] for f in os.listdir("ducks") if f.endswith('.ducky')]
    except OSError:
        # If SD card is unavailable, list files from root directory
        ducky_files = ["ducks/" +f[:-6] for f in os.listdir("ducks") if f.endswith('.ducky')]

    rubber_ducky_submenu = ducky_files  # Update the submenu with the list of files

def load_captive_portal_folders():
    global captive_portal_list
    captive_portals = []  # Reset the list of portals

    # Try to list folders from the SD card directory
    try:
        captive_portals = ["/sd/portals/" + f for f in os.listdir("/sd/portals")]
        captive_portals += ["portals/" + f for f in os.listdir("portals")]
    except OSError:
        # If SD card is unavailable, list folders from root directory
        captive_portals = ["portals/" + f for f in os.listdir("portals")]

    captive_portal_list = captive_portals  # Update the list of captive portals

# Display the menu on the screen
def display_menu(menu):
    global scroll_offset, last_scroll_time
    # Dynamically allocate framebuffer
    width = 160
    height = 128
    fb = framebuf.FrameBuffer(bytearray(width * height * 2), width, height, framebuf.RGB565)
    fb.fill(BLACK)

    for i in range(max_display_items):
        option_index = display_start_index + i
        if option_index >= len(menu):
            break
        y = initial_y_position + i * 20

        text = menu[option_index]
        if option_index == selected_index:
            if len(text) > 14:
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_scroll_time) >= 500:
                    visible_text = text[scroll_offset:scroll_offset + 14]
                    scroll_offset += 1
                    if scroll_offset > len(text) - 14:
                        scroll_offset = 0
                    last_scroll_time = current_time
                else:
                    visible_text = text[scroll_offset:scroll_offset + 14]
            else:
                visible_text = text
                scroll_offset = 0  # Reset scrolling if text fits
            # Highlight the selected option
            fb.fill_rect(10, y - 4, 140, 16, WHITE)  # Inverse color: White background
            fb.text(visible_text, 20, y, BLACK)  # Text in black
        else:
            fb.text(text, 20, y, WHITE)  # Non-selected options in white

    ST7735.update_display(fb)
    del fb  # Free framebuffer memory

# Display the Interval menu
def display_interval_menu():
    global interval_value
    # Dynamically allocate framebuffer
    width = 160
    height = 128
    fb = framebuf.FrameBuffer(bytearray(width * height * 2), width, height, framebuf.RGB565)
    fb.fill(BLACK)

    # Display "Interval (ms)" at the top
    fb.text("Interval (ms)", 25, 10, WHITE)

    # Display and highlight the interval value in the middle
    interval_str = "{:03d}".format(interval_value)
    fb.fill_rect(50, 50, 50, 20, WHITE)  # Inverse color: White background
    fb.text(interval_str, 63, 57, BLACK)  # Text in black

    ST7735.update_display(fb)
    del fb  # Free framebuffer memory

# Display the Loop Interval menu
def display_loop_interval_menu():
    global loop_interval_value
    # Dynamically allocate framebuffer
    width = 160
    height = 128
    fb = framebuf.FrameBuffer(bytearray(width * height * 2), width, height, framebuf.RGB565)
    fb.fill(BLACK)

    # Display "Loop Interval (sec)" at the top
    fb.text("Loop Interval (sec)", 5, 10, WHITE)

    # Display and highlight the loop interval value in the middle
    loop_interval_str = "{:01d}".format(loop_interval_value)
    fb.fill_rect(50, 50, 50, 20, WHITE)  # Inverse color: White background
    fb.text(loop_interval_str, 71, 57, BLACK)  # Text in black

    ST7735.update_display(fb)
    del fb  # Free framebuffer memory

# Display "Attack Running!" message
def display_attack_running():
    # Dynamically allocate framebuffer
    width = 160
    height = 128
    fb = framebuf.FrameBuffer(bytearray(width * height * 2), width, height, framebuf.RGB565)
    fb.fill(BLACK)

    # Display "Attack Running!" in the middle of the screen
    fb.text("Attack Running!", 20, 50, WHITE)

    ST7735.update_display(fb)
    del fb  # Free framebuffer memory

# Enter a new menu
def enter_menu(new_menu):
    global current_menu, selected_index, display_start_index, previous_menu_stack
    previous_menu_stack.append((current_menu, selected_index, display_start_index))
    current_menu = new_menu
    selected_index = 0
    display_start_index = 0
    display_menu(current_menu)

# Exit the current menu
def exit_menu():
    global current_menu, selected_index, display_start_index, previous_menu_stack
    current_menu, selected_index, display_start_index = previous_menu_stack.pop()
    display_menu(current_menu)

# Handle Interval menu interactions
def handle_interval_menu():
    global interval_value

    display_interval_menu()  # Display the interval menu at the start
    time.sleep(0.2)  # Delay to prevent accidental double input

    while True:
        if any(not btn.value() for btn in button_up):
            flash_status_light()  # Flash status light on button press
            if interval_value < 950:
                interval_value += 50
            display_interval_menu()
            time.sleep(0.2)  # Debounce delay
        elif any(not btn.value() for btn in button_down):
            flash_status_light()  # Flash status light on button press
            if interval_value > 50:
                interval_value -= 50
            display_interval_menu()
            time.sleep(0.2)  # Debounce delay
        elif any(not btn.value() for btn in button_right):
            flash_status_light()  # Flash status light on button press
            handle_loop_interval_menu()  # Move to the loop interval menu
            break  # Exit the interval menu loop
        elif any(not btn.value() for btn in button_left):
            flash_status_light()  # Flash status light on button press
            time.sleep(0.2)  # Debounce delay
            break  # Exit the interval menu loop

# Handle Loop Interval menu interactions
def handle_loop_interval_menu():
    global loop_interval_value

    display_loop_interval_menu()  # Display the loop interval menu at the start
    time.sleep(0.2)  # Delay to prevent accidental double input

    while True:
        if any(not btn.value() for btn in button_up):
            flash_status_light()  # Flash status light on button press
            if loop_interval_value < 9:
                loop_interval_value += 1
            display_loop_interval_menu()
            time.sleep(0.2)  # Debounce delay
        elif any(not btn.value() for btn in button_down):
            flash_status_light()  # Flash status light on button press
            if loop_interval_value > 1:
                loop_interval_value -= 1
            display_loop_interval_menu()
            time.sleep(0.2)  # Debounce delay
        elif any(not btn.value() for btn in button_left):
            flash_status_light()  # Flash status light on button press
            time.sleep(0.2)  # Debounce delay
            handle_interval_menu()  # Return to the interval menu
            break  # Exit the loop interval menu loop
        elif any(not btn.value() for btn in button_right):
            flash_status_light()  # Flash status light on button press
            start_attack()  # Start the attack in the background
            break  # Exit the loop interval menu loop

# Start advertising thread for AppleJuice attack
def start_attack():
    pwm_status_light.duty_u16(65535 // 8)  # Keep status light on during attack
    display_attack_running() # Show the "Attack Running!" message
    applejuice.startup(payload_selected_index, interval_value, loop_interval_value) # Start the attack
    pwm_status_light.duty_u16(0)  # Turn off the status light when attack stops
    exit_menu()

# Captive Portal Test
def handle_captive_portal(selected_path):
    pwm_status_light.duty_u16(65535 // 8)  # Keep status light on during attack
    display_attack_running()  # Show the "Attack Running!" message
    captivewifi.startup(selected_path) # Start captive portal in main thread due to weird wifi limitations
    pwm_status_light.duty_u16(0)  # Turn off the status light when attack stops
    exit_menu()  # Exit back to the previous menu

# Button Handling Updated for Captive Portal
def check_buttons():
    global selected_index, display_start_index, payload_selected_index

    button_pressed = False

    if any(not btn.value() for btn in button_up):
        flash_status_light()  # Flash status light on button press
        if selected_index > 0:
            selected_index -= 1
            if selected_index < display_start_index:
                display_start_index -= 1
        else:
            selected_index = len(current_menu) - 1
            display_start_index = max(0, len(current_menu) - max_display_items)
        button_pressed = True
        time.sleep(0.2)  # Debounce delay
    elif any(not btn.value() for btn in button_down):
        flash_status_light()  # Flash status light on button press
        if selected_index < len(current_menu) - 1:
            selected_index += 1
            if selected_index >= display_start_index + max_display_items:
                display_start_index += 1
        else:
            selected_index = 0
            display_start_index = 0
        button_pressed = True
        time.sleep(0.2)  # Debounce delay
    elif any(not btn.value() for btn in button_right):
        flash_status_light()  # Flash status light on button press
        if current_menu == main_menu:
            if current_menu[selected_index] == "WiFi":
                enter_menu(wifi_submenu)
            elif current_menu[selected_index] == "Bluetooth":
                enter_menu(bluetooth_submenu)
            elif current_menu[selected_index] == "USB":
                enter_menu(usb_submenu)
        elif current_menu == wifi_submenu and current_menu[selected_index] == "Captive Portal":
            enter_menu(captive_portal_list)
        elif current_menu == captive_portal_list:
            selected_path = captive_portal_list[selected_index]
            handle_captive_portal(selected_path)
        elif current_menu == bluetooth_submenu and current_menu[selected_index] == "AppleJuice":
            enter_menu(payload_names)
        elif current_menu == payload_names:
            payload_selected_index = selected_index
            handle_interval_menu()  # Move to the interval menu
        elif current_menu == usb_submenu and current_menu[selected_index] == "Rubber Ducky":
            enter_menu(rubber_ducky_submenu)
        elif current_menu == rubber_ducky_submenu:
            selected_script = rubber_ducky_submenu[selected_index] + ".ducky"  # Get the full filename
            interpret_ducky_script(selected_script)  # Execute the script
        button_pressed = True
        time.sleep(0.2)  # Debounce delay
    elif any(not btn.value() for btn in button_left) and previous_menu_stack:
        flash_status_light()  # Flash status light on button press
        exit_menu()
        button_pressed = True
        time.sleep(0.2)  # Debounce delay

    if button_pressed:
        display_menu(current_menu)  # Update the display immediately if a button is pressed

# Start Menu Updated to Load Captive Portals
def start_menu():
    load_ducky_scripts()  # Load .ducky files at startup
    load_captive_portal_folders()  # Load captive portal folders at startup
    while True:
        check_buttons()
        display_menu(current_menu)
        time.sleep(0.05)  # Short delay to control button check speed

# Initialize and display
ST7735.init_display()
ST7735.mount_sd()
start_menu()
