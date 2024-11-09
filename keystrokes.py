import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode
import time

# Initialize the keyboard interface
keyboard = KeyboardInterface()
usb.device.get().init(keyboard, builtin_driver=True)

# Map characters to KeyCodes, Will add more in future
CHARACTER_TO_KEYCODE = {
    'a': KeyCode.A,
    'b': KeyCode.B,
    'c': KeyCode.C,
    'd': KeyCode.D,
    'e': KeyCode.E,
    'f': KeyCode.F,
    'g': KeyCode.G,
    'h': KeyCode.H,
    'i': KeyCode.I,
    'j': KeyCode.J,
    'k': KeyCode.K,
    'l': KeyCode.L,
    'm': KeyCode.M,
    'n': KeyCode.N,
    'o': KeyCode.O,
    'p': KeyCode.P,
    'q': KeyCode.Q,
    'r': KeyCode.R,
    's': KeyCode.S,
    't': KeyCode.T,
    'u': KeyCode.U,
    'v': KeyCode.V,
    'w': KeyCode.W,
    'x': KeyCode.X,
    'y': KeyCode.Y,
    'z': KeyCode.Z,
    ' ': KeyCode.SPACE,
}

def type_message(message):
    for char in message.lower():  # Convert message to lowercase to match keycodes for now (need to figure out how to press shift)
        if char in CHARACTER_TO_KEYCODE:
            keycode = CHARACTER_TO_KEYCODE[char]
            keyboard.send_keys([keycode])
            time.sleep(0.1)  # Short delay to simulate typing speed
            keyboard.send_keys([])  # Release the key
        else:
            print(f"Character '{char}' not found in keycode mapping.")

# Example function to test typing "test", Change this to test your own message
def test_payload():
    type_message("test")
