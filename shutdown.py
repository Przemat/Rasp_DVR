#!/usr/bin/python3
from pijuice import PiJuice 
import os 
pijuice = PiJuice(1, 0x14)
# Remove power to PiJuice MCU IO pins
pijuice.power.SetSystemPowerSwitch(0)
# Set wakeup
pijuice.power.SetWakeUpOnCharge(0.0)
# Remove 5V power to RPi after 60 seconds
pijuice.power.SetPowerOff(60)
# Shut down the RPi
os.system("sudo halt")
