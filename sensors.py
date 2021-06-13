# BH1750 Documentation: https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
# SG90 Documentation : http://www.ee.ic.ac.uk/pcheung/teaching/DE1_EE/stores/sg90_datasheet.pdf

from machine import I2C, Pin, PWM
import time

class BH1750NotFoundError(Exception): pass

class BH1750(): # light intensity sensor
       
    def __init__(self, id=0, scl=17, sda=16):
        """
        Initialize the BH1750 light intensity sensor. Use the Raspberry Pi
        Pico Pinout to wire the sensor.
        Input:
            id : id of the I2C connection. Ex: for an I2C0 connection, id = 0
            scl : number of the SCL Pin, for the 22th pin, use 17 (see pinout)
            sda : same as scl
        """

        self.HIGH_RESOLUTION = 0x11 # 0.5 Lux precision, measure time: 120 ms
        self.HIGH_RESOLUTION_2 = 0x10 # 1 Lux precision, measure time: 120 ms
        self.LOW_RESOLUTION = 0x13 # # 4 Lux précision, measure time: 16s

        self.ONE_HIGH = 0x21 # 1 measure then idle
        self.ONE_HIGH_2 = 0x20
        self.ONE_LOW = 0x23

        self.i2c = I2C(id, scl=Pin(scl), sda=Pin(sda))
        self.count = 0

        if self.detect():
            if self.address == 0x5C:
                self.mode = self.LOW_RESOLUTION
            else:
                self.mode = self.HIGH_RESOLUTION
            self.reset()
        else:
            raise BH1750NotFoundError("Please check the connections of the BH1750 or the scl and sda arguments sent to the class.")
        
    def detect(self):
        """
        Returns a boolean on whether or not the sensor is detected.
        """

        i2c_peripherals = self.i2c.scan()
        for i2c_peripheral in i2c_peripherals:    
            if i2c_peripheral in [0x5C, 0x23]: # low vs high mode
                self.address = i2c_peripheral
                print("BH1750 address " + str(self.address))
                return True
        return False
    
    def reset(self):
        """Reset the connection. Use it to lower the power consumption once
        you do not use the sensor.
        Returns nothing.
        """

        data = bytearray(1)
        data[0] = 0x01 # Power on
        self.i2c.writeto(self.address, data)  
        time.sleep(0.01)
        data[0] = 0x07 # reset
        self.i2c.writeto(self.address, data)  
        time.sleep(0.01)

        if self.mode == self.LOW_RESOLUTION:
            self.measure(self.ONE_LOW)
            time.sleep(0.024)
        else:
            self.measure(self.ONE_HIGH)
            time.sleep(0.18)
    
    def measure(self, mode=False):
        """Returns the light intensity that the sensor receives.
        Input:
            mode : the measurement mode (see self.__init__)
        Returns:
            lux : light intensity
        """

        if not mode:
            mode = self.mode

        data_mode = bytearray(1)
        lux = bytearray(2)
        delay = 0 

        if mode in (self.ONE_HIGH, self.ONE_HIGH_2):
            delay = 0.12
        if mode == self.ONE_LOW:
            delay = 0.016

        data_mode[0] = mode
        self.i2c.writeto(self.address, data_mode)
        time.sleep(delay)

        self.i2c.readfrom_into(self.address, lux)

        lux = lux[0] * 256 + lux[1]
        lux = round(lux / 1.2, 1)

        return lux

class SG90(): # servomotor
    def __init__(self, pin=0):
        """
        Initialize the servo motor.
        Input:
            pin: the number in which the PWM wire of the sensor is plugged into
        """

        self.servo = PWM(Pin(pin))
        self.servo.freq(50)
        duty = self.servo.duty_u16()
        self.position = round((duty-3276) * 90 / 3277)

    def move(self, angle=0):
        """
        Move the servomotor to a certain degree. The range is 0-90 degrees
        because my servomotor doesn’t support 180 degrees rotations.
        Input:
            angle: the angle in which the servo motor should be.
        """

        if angle < 0 or angle > 90:
            return "Wrong angle."

        self.position = angle

        duty = 3276 + angle * 3277 / 90 # 3277 = 6553 - 3276
        self.servo.duty_u16(round(duty))
