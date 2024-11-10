import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode
import time

# Initialize the keyboard interface
keyboard = KeyboardInterface()
usb.device.get().init(keyboard, builtin_driver=True)

keypress_delay = 0  # Delay in seconds between keypresses, supports decimal values

# Modifier keys dictionary
MODIFIER_KEYS = {
    'CTRL': KeyCode.LEFT_CTRL,
    'SHIFT': KeyCode.LEFT_SHIFT,
    'ALT': KeyCode.LEFT_ALT,
    'GUI': KeyCode.LEFT_UI,  # Commonly represents the Windows key
}

# Special keys dictionary
SPECIAL_KEYS = {
    'ENTER': KeyCode.ENTER,
    'DELETE': KeyCode.DELETE,
    'ESCAPE': KeyCode.ESCAPE,
    'UP': KeyCode.UP,
    'DOWN': KeyCode.DOWN,
    'LEFT': KeyCode.LEFT,
    'RIGHT': KeyCode.RIGHT,
    'BACKSPACE': KeyCode.BACKSPACE,
    'F1': KeyCode.F1,
    'F2': KeyCode.F2,
    'F3': KeyCode.F3,
    'F4': KeyCode.F4,
    'F5': KeyCode.F5,
    'F6': KeyCode.F6,
    'F7': KeyCode.F7,
    'F8': KeyCode.F8,
    'F9': KeyCode.F9,
    'F10': KeyCode.F10,
    'F11': KeyCode.F11,
    'F12': KeyCode.F12,
}

# Map characters to KeyCodes
CHARACTER_TO_KEYCODE = {
    'a': KeyCode.A, 'b': KeyCode.B, 'c': KeyCode.C, 'd': KeyCode.D, 'e': KeyCode.E,
    'f': KeyCode.F, 'g': KeyCode.G, 'h': KeyCode.H, 'i': KeyCode.I, 'j': KeyCode.J,
    'k': KeyCode.K, 'l': KeyCode.L, 'm': KeyCode.M, 'n': KeyCode.N, 'o': KeyCode.O,
    'p': KeyCode.P, 'q': KeyCode.Q, 'r': KeyCode.R, 's': KeyCode.S, 't': KeyCode.T,
    'u': KeyCode.U, 'v': KeyCode.V, 'w': KeyCode.W, 'x': KeyCode.X, 'y': KeyCode.Y,
    'z': KeyCode.Z, ' ': KeyCode.SPACE,
    '0': KeyCode.N0, '1': KeyCode.N1, '2': KeyCode.N2, '3': KeyCode.N3, '4': KeyCode.N4,
    '5': KeyCode.N5, '6': KeyCode.N6, '7': KeyCode.N7, '8': KeyCode.N8, '9': KeyCode.N9,
    '-': KeyCode.MINUS, '=': KeyCode.EQUAL, '[': KeyCode.OPEN_BRACKET, ']': KeyCode.CLOSE_BRACKET,
    '\\': KeyCode.BACKSLASH, ';': KeyCode.SEMICOLON, '\'': KeyCode.QUOTE, '`': KeyCode.GRAVE,
    ',': KeyCode.COMMA, '.': KeyCode.DOT, '/': KeyCode.SLASH, '\n': KeyCode.ENTER, '\t': KeyCode.TAB
}

# Special characters that require Shift modifier
SHIFT_REQUIRED_CHARACTERS = {
    '!': KeyCode.N1, '@': KeyCode.N2, '#': KeyCode.HASH, '$': KeyCode.N4,
    '%': KeyCode.N5, '^': KeyCode.N6, '&': KeyCode.N7, '*': KeyCode.N8,
    '(': KeyCode.N9, ')': KeyCode.N0, '_': KeyCode.MINUS, '+': KeyCode.EQUAL,
    '{': KeyCode.OPEN_BRACKET, '}': KeyCode.CLOSE_BRACKET, '|': KeyCode.BACKSLASH,
    ':': KeyCode.SEMICOLON, '"': KeyCode.QUOTE, '<': KeyCode.COMMA, '>': KeyCode.DOT,
    '?': KeyCode.SLASH
}

def send_string(text):
    # Send a string character by character
    for char in text:
        if char.islower() or char.isdigit() or char in CHARACTER_TO_KEYCODE:
            # Send lowercase letters, digits, and space
            keycode = CHARACTER_TO_KEYCODE[char.lower()]
            keyboard.send_keys([keycode])
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release the key
        elif char.isupper():
            # Send uppercase letters with Shift
            keycode = CHARACTER_TO_KEYCODE[char.lower()]
            keyboard.send_keys([MODIFIER_KEYS['SHIFT'], keycode])
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
        elif char in SHIFT_REQUIRED_CHARACTERS:
            # Send special characters with Shift
            keycode = SHIFT_REQUIRED_CHARACTERS[char]
            keyboard.send_keys([MODIFIER_KEYS['SHIFT'], keycode])
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
        else:
            print(f"Character '{char}' not found in keycode mapping.")

def interpret_ducky_script(filename):
    # Interpret a DuckyScript file and execute commands
    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Ignore lines that start with 'REM' as comments
        if line.strip().startswith('REM'):
            continue

        parts = line.strip().split()
        command = parts[0].upper()

        if command == 'STRING' and len(parts) > 1:
            # Send a string
            send_string(" ".join(parts[1:]))
        elif command in SPECIAL_KEYS:
            # Handle special keys
            keyboard.send_keys([SPECIAL_KEYS[command]])
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release key
        elif command == 'DELAY' and len(parts) > 1:
            # Delay for a specified time in milliseconds
            delay_time = int(parts[1]) / 1000.0
            time.sleep(delay_time)
        elif command in MODIFIER_KEYS:
            # Handle multiple modifier keys with a final key (ex. "CTRL ALT DELETE")
            modifiers = []
            keycode = None

            # Collect all modifiers and final key from the command
            for part in parts:
                part_upper = part.upper()
                if part_upper in MODIFIER_KEYS:
                    modifiers.append(MODIFIER_KEYS[part_upper])
                elif part_upper in SPECIAL_KEYS:
                    keycode = SPECIAL_KEYS[part_upper]
                elif part.lower() in CHARACTER_TO_KEYCODE:
                    keycode = CHARACTER_TO_KEYCODE[part.lower()]
                elif part in SHIFT_REQUIRED_CHARACTERS:
                    modifiers.append(MODIFIER_KEYS['SHIFT'])
                    keycode = SHIFT_REQUIRED_CHARACTERS[part]

            # If we have modifiers and a keycode, send them together
            if modifiers and keycode:
                keyboard.send_keys(modifiers + [keycode])
                time.sleep(keypress_delay)
                keyboard.send_keys([])  # Release keys
            elif modifiers:
                # If only modifiers were specified, press and release them alone
                keyboard.send_keys(modifiers)
                time.sleep(keypress_delay)
                keyboard.send_keys([])  # Release keys
            else:
                print(f"No key specified for modifiers in command '{line.strip()}'")
        else:
            print(f"Command '{command}' not recognized or not implemented.")
