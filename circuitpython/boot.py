import board, digitalio


import usb_hid

# These are the default devices, so you don't need to write
# this explicitly if the default is what you want.
usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.CONSUMER_CONTROL)
)


button = digitalio.DigitalInOut(board.GP10)
button.pull = digitalio.Pull.UP

# Disable devices only if button is not pressed.
if button.value:
    import storage
    print("Button 6 not pressed, disabling drive")
    storage.disable_usb_drive()
    import usb_midi
    import usb_cdc

    usb_midi.disable()
    usb_cdc.disable()   # Disable both serial devices.

