
import time
from adafruit_bus_device.i2c_device import I2CDevice

class DellDisplay:
    # DDC Variables
    DDC_ADDRESS = 0x37

    VPC_INPUT = 0x60
    VPC_PBP_INPUT = 0xe8
    VPC_PBP_MODE = 0xe9
    VPC_SWITCH_USB = 0xe7
    VPC_VOLUME = 0x62
    VPC_POWER = 0xd6

    # Dell specific 
    HDMI1 = 0x11
    HDMI2 = 0x12
    DP1 = 0x0f
    USBC = 0x1b

    mode_to_text = {HDMI1: "H1", HDMI2: "H2", DP1: "DP", USBC: "C"}

    # 0xe7
    SWITCH_USB = 0xff00

    # 0xe9
    MODE_PBP = 0x24
    MODE_OFF = 0x00
    def __init__(self, i2c) -> None:

        self._i2c = i2c
        self._input = 0
        self._pbp_input = None
        self._current_power = None
        self.connect()
    
    def connect(self):
        try:
            self.i2c_device = I2CDevice(self._i2c, DellDisplay.DDC_ADDRESS)
            self.connected = True
        except ValueError:
            self.i2c_device = None
            self.connected = False
    
    def getVPC(self, op):
        #while not self.i2c.try_lock():
        #    pass
        with self.i2c_device as i2c:
            try:
                data = bytearray((0x51, 0x82, 0x01, op, 0))
                result = bytearray(12)

                checksum = (DellDisplay.DDC_ADDRESS << 1)
                for a in data:
                    checksum^=a
                data[-1]=checksum
                i2c.write(bytes(data))
                time.sleep(0.05)
                i2c.readinto(result)
                return (result[8] << 8) + result[9]
            except OSError:
                self.connected = False
            #finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
              #  pass
                #self.i2c.unlock()

    def setVPC(self, op, value):
        with self.i2c_device as i2c:
            # while not i2c.try_lock():
            #     pass

            try:
                data = bytearray((0x51, 0x84, 0x03, op, value >> 8, value % 256, 0))
                checksum = (DellDisplay.DDC_ADDRESS << 1)
                for a in data:
                    checksum^=a
                data[-1]=checksum
                i2c.write(bytes(data))
                time.sleep(0.05)
            except OSError:
                self.connected = False

            #finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
                #i2c.unlock()

    def toggle_pbp(self):
        global current_pbp_mode
        if current_pbp_mode == DellDisplay.MODE_PBP:
            self.setVPC(DellDisplay.VPC_PBP_MODE, DellDisplay.MODE_OFF)
            current_pbp_mode = DellDisplay.MODE_OFF
        else:
            self.setVPC(DellDisplay.VPC_PBP_MODE, DellDisplay.MODE_PBP)
            current_pbp_mode = DellDisplay.MODE_PBP
        #self.update_display()

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        if self._input != value:
            self.setVPC(DellDisplay.VPC_INPUT, value)
            self._input = value
    
    @property
    def pbp_input(self):
        return self._pbp_input

    @pbp_input.setter
    def pbp_input(self, value):
        if self._input != value:
            self.setVPC(DellDisplay.VPC_PBP_INPUT, value)
            self._pbp_input = value
    
    @property
    def pbp_mode(self):
        return self._pbp_mode

    @pbp_mode.setter
    def pbp_mode(self, value):
        self._pbp_mode = self.getVPC(DellDisplay.VPC_PBP_MODE) % 256
        if self._pbp_mode != value:
            self.setVPC(DellDisplay.VPC_PBP_MODE, value)
            self._pbp_mode = value
            time.sleep(1.0)
    

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self.setVPC(DellDisplay.VPC_VOLUME, value)
        self._volume = value

    @property 
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self.setVPC(DellDisplay.VPC_POWER, value)
        self._power = value

    def toggle_usb(self):
        self.setVPC(DellDisplay.VPC_SWITCH_USB, DellDisplay.SWITCH_USB)


    def update_monitor_status(self):
        #global current_pbp_input, current_input, current_pbp_mode, current_power
        #encoder.position=getVPC(0x62)
        if self.connected:
            self._volume = self.getVPC(DellDisplay.VPC_VOLUME)
            self._pbp_mode = self.getVPC(DellDisplay.VPC_PBP_MODE) % 256
            self._input = self.getVPC(DellDisplay.VPC_INPUT) % 256
            #print(self.current_input)
            self._pbp_input = self.getVPC(DellDisplay.VPC_PBP_INPUT) % 256
            self._power = self.getVPC(DellDisplay.VPC_POWER)
        else:
            self._volume = None
            self._pbp_mode = None
            self._pbp_input = None
            self._power = None
            self.connect()
