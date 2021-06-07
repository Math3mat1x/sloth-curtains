import machine, time
import bh1750

i2c = machine.I2C(id = 0, scl = machine.Pin(17), sda = machine.Pin(16), freq=400000)

sensor = bh1750.BH1750(i2c)  # declaration BH1750

def luminosity_test():
    for _ in range(10):
        measure = sensor.measure()
        print(measure)
        time.sleep(1)
