from machine import I2C, Pin
import time

BH1750_ADDRESS_ADD_LOW  = 0x5C
BH1750_ADDRESS_ADD_HIGH = 0x23
BH1750_POWER_DOWN = 0x00  # Mise en veille
BH1750_POWER_ON = 0x01  # Attente pour une commande
BH1750_RESET = 0x07  # Mise à 0 du registre de données seulement en mode POWER_ON
# Mesure continue, résolution 1 Lux, temps de mesure 120ms
MODE_CONTINU_HAUTE_RESOLUTION = 0x10
# Mesure continue, résolution 0.5 Lux, temps de mesure 120ms
MODE_2_CONTINU_HAUTE_RESOLUTION = 0x11
# Mesure continue, résolution 4 Lux, temps de mesure 16ms
MODE_CONTINU_BASSE_RESOLUTION = 0x13
# 1 mesure puis passe en veille, résolution 1 Lux, temps de mesure 120ms
MODE_UNE_MESURE_HAUTE_RESOLUTION = 0x20
# 1 mesure puis passe en veille, résolution 0.5 Lux, temps de mesure 120ms
MODE_2_UNE_MESURE_HAUTE_RESOLUTION = 0x21
# 1 mesure puis passe en veille, résolution 4 Lux, temps de mesure 16ms
MODE_UNE_MESURE_BASSE_RESOLUTION = 0x23 

class BH1750():
       
    def __init__(self, i2c):
        self.i2c = i2c
        if self.detect():
            self.reset()
        
    def detect(self):
        detect_bh1750 = False
        i2c_peripheriques = self.i2c.scan()
        for i2c_peripherique in i2c_peripheriques:    
            if (i2c_peripherique == BH1750_ADDRESS_ADD_LOW):
                self.adresse = BH1750_ADDRESS_ADD_LOW
                detect_bh1750 = True
            if (i2c_peripherique == BH1750_ADDRESS_ADD_HIGH):
                self.adresse = BH1750_ADDRESS_ADD_HIGH
                detect_bh1750 = True
        return detect_bh1750
    
    def reset(self):
        self.data = bytearray(1)
        self.data[0] = BH1750_POWER_ON
        self.i2c.writeto(self.adresse, self.data)  
        time.sleep(0.01)  # delai de 10ms
        self.data[0] = BH1750_RESET
        self.i2c.writeto(self.adresse, self.data)  
        time.sleep(0.01)  # delai de 10ms
    
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
