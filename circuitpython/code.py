
import board
import digitalio
import time
import rotaryio
import busio
import displayio
import asyncio
import supervisor

import busio
from adafruit_display_shapes.rect import Rect
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

from adafruit_debouncer import Debouncer

from dell_display import DellDisplay

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


import adafruit_displayio_sh1106
displayio.release_displays()

i2c_display = busio.I2C(board.GP15, board.GP14, frequency=500000)


# INIT DISPLAY
# Should be done first, because we can see errors there.
display_bus = displayio.I2CDisplay(i2c_display, device_address=0x3C)

WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_sh1106.SH1106(display_bus, colstart=2 , width=WIDTH, height=HEIGHT, rotation=180)
#display.brightness = 1.00

# Make the display context
default_display = displayio.Group()
empty_display = displayio.Group()
display.show(default_display)

BLACK = 0x000000
WHITE = 0xFFFFFF
#font = bitmap_font.load_font("/font/Helvetica-Bold-16.bdf")
font = terminalio.FONT

volume_label = Label(font, text="Brightness", color=WHITE)
volume_label.anchor_point = (0.0, 0.0)
volume_label.anchored_position = (0, 3)
desk_label = Label(font, text="??? cm", color=WHITE)
desk_label.anchor_point = (1.0, 1.0)
desk_label.anchored_position = (127, 64)

input_label = Label(font, text="????", color=WHITE, scale=2)
input_label.anchor_point = (1.0, 0.0)
input_label.anchored_position = (127, 3)

default_display.append(volume_label)
default_display.append(desk_label)
default_display.append(input_label)


def make_pin_reader(pin):
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.UP
    return lambda: io.value


# ENCODER

encoder = rotaryio.IncrementalEncoder(board.GP2, board.GP3, divisor=4)
encoder_button = Debouncer(make_pin_reader(board.GP4))
last_position = None

# BUTTONS

button1 = Debouncer(make_pin_reader(board.GP5))
button2 = Debouncer(make_pin_reader(board.GP6))
button3 = Debouncer(make_pin_reader(board.GP7))
button4 = Debouncer(make_pin_reader(board.GP8))
button5 = Debouncer(make_pin_reader(board.GP9))
button6 = Debouncer(make_pin_reader(board.GP10))

to_update = (encoder_button, button1, button2, button3, button4, button5, button6)

# Set up a keyboard device.
kbd = None
if supervisor.runtime.usb_connected:
    kbd = Keyboard(usb_hid.devices)

# DELL DISPLAY

i2c_ddc = busio.I2C(board.GP13, board.GP12, frequency=100000)
dell = DellDisplay(i2c_ddc)

# TODO: Desk Integration
#desk_uart = busio.UART(board.GP8, board.GP9, baudrate=115200, timeout=0)

DESK_OFFSET = 3

def refresh_display_labels():
    if dell.power == 5:
        #turn off
        display.show(empty_display)
        display.auto_refresh=False
        display.refresh()
    else:
        text = "??"
        tmp = dell.input
        if dell.input in DellDisplay.mode_to_text:
            text = dell.mode_to_text[tmp]

        if dell.pbp_mode == DellDisplay.MODE_PBP:
            if dell.pbp_input in dell.mode_to_text:
                text = text + "+" + DellDisplay.mode_to_text[dell.pbp_input]

        input_label.text = text
        display.show(default_display)
        display.auto_refresh=True
        #display.




dell.update_monitor_status()
refresh_display_labels()

i=0

switched_pbp = False

while True:
    i+=1
    if i>=1000:
        dell.update_monitor_status()
        refresh_display_labels()
        i=0
    
    for b in to_update:
        b.update()

    #if encoder_button.rose:
    #    print("rose")
    if encoder_button.fell:
        print("fell")
    if button1.fell:
        if button6.value:
            dell.input = DellDisplay.USBC
        else:
            dell.pbp_mode = DellDisplay.MODE_PBP
            dell.pbp_input = DellDisplay.USBC
            switched_pbp = True
    if button2.fell:
        if button6.value:
            dell.input = DellDisplay.DP1
        else:
            dell.pbp_mode = DellDisplay.MODE_PBP
            dell.pbp_input = DellDisplay.DP1
            switched_pbp = True
    if button3.fell:
        if button6.value:
            dell.input = DellDisplay.HDMI1
        else:
            dell.pbp_mode = DellDisplay.MODE_PBP
            dell.pbp_input = DellDisplay.HDMI1
            switched_pbp = True
    if button4.fell and kbd is not None:
        kbd.press(Keycode.F13)
    if button4.rose and kbd is not None:
        kbd.release(Keycode.F13)
    if button5.fell:
        dell.toggle_usb()

    if button6.rose:
        if switched_pbp:
            switched_pbp = False
        elif dell.pbp_mode == DellDisplay.MODE_PBP:
            dell.pbp_mode = DellDisplay.MODE_OFF
            print("PBP Switched off")
    
    position = encoder.position
    if last_position is None or position != last_position:
        if position <=0:
            position = 0
            encoder.position = 0
        if position >= 100:
            encoder.position = 100
            position = 100
        volume_label.text = "Volume %d%%" % position
    last_position = position
    
    #desk_data = None
    # if desk_uart.in_waiting > 5:
    #     desk_data = desk_uart.read()
    #     if desk_data is not None:
    #         printable = [int(a) for a in desk_data]
    #         print(printable)
    #         if len(desk_data) > 6 and desk_data[0] == 5 and desk_data[1] == 2:
    #             desk_height = desk_data[4]
    #             desk_label.text = "%d cm" % (desk_height - DESK_OFFSET)
