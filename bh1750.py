# BH1750 Documentation: https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf

from machine import I2C, Pin
import time

HIGH_RESOLUTION = 0x11 # 0.5 Lux precision, measure time: 120 ms
HIGH_RESOLUTION_2 = 0x10 # 1 Lux precision, measure time: 120 ms
LOW_RESOLUTION = 0x13 # # 4 Lux précision, measure time: 16s

ONE_HIGH = 0x21 # 1 measure then idle
ONE_HIGH_2 = 0x20
ONE_LOW = 0x23

class BH1750():
       
    def __init__(self, i2c):
        self.i2c = i2c
        if self.detect():
            self.reset()
        
    def detect(self):
        i2c_peripherals = self.i2c.scan()
        for i2c_peripheral in i2c_peripherals:    
            if i2c_peripheral in [0x5C, 0x23]: # low vs high mode
                self.address = i2c_peripheral
                print("BH1750 address " + str(self.address))
                return True
        return detect_bh1750
    
    def reset(self):
        data = bytearray(1)
        data[0] = 0x01 # Power on
        self.i2c.writeto(self.address, data)  
        time.sleep(0.01)
        data[0] = 0x07 # reset
        self.i2c.writeto(self.address, data)  
        time.sleep(0.01)
    
    def measure(self, mode=False):
        if not mode:
            if self.address == 0x5C:
                mode = LOW_RESOLUTION
            else:
                mode = HIGH_RESOLUTION

        data_mode = bytearray(1)
        lux = bytearray(2)
        delay = 0 

        if mode in (ONE_HIGH, ONE_HIGH_2):
            delay = 0.12
        if mode == ONE_LOW:
            delay = 0.016

        data_mode[0] = mode
        self.i2c.writeto(self.address, data_mode)
        time.sleep(delay)

        self.i2c.readfrom_into(self.address, lux)

        lux = lux[0] * 256 + lux[1]
        return round(lux / 1.2, 1)
