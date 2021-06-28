import asyncio
import os

import obd
import bluetooth, subprocess

class OBD:
    def __init__(self):
        self.connected = True
        self.is_obd = False
        self.speed, self.rpm, self.el, self.coolant_temp, self.error = "","","","",[]
    async def set_obd(self):

        # Start a new "bluetooth-agent" process where XXXX is the passkey
        try:
            os.system("sudo rfcomm release 0")
            os.system("sudo rfcomm bind 0 AA:BB:CC:DD:EE:FF")
        finally:
            self.connected = True
            self.connection = obd.OBD()
        while self.connected:
            try:
                self.speed = self.connection.query(obd.commands.SPEED)
                self.rpm = self.connection.query(obd.commands.RPM)
                self.el = self.connection.query(obd.commands.ENGINE_LOAD)
                self.coolant_temp = self.connection.query(obd.commands.COOLANT_TEMP)
                self.error = self.connection.query(obd.commands.GET_DTC)
                if(self.speed == "None" or self.rpm == "None" or self.el == "None"):
                    self.connection = obd.OBD()
                    self.is_obd = False
                else:
                    self.is_obd = True

            except:
                self.connection = obd.OBD()
    def get_obd(self):
        print(self.speed)
        return self.speed, self.rpm, self.el, self.coolant_temp, self.error


