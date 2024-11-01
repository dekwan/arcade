import sys

import serial

class LED:
    RED = 0
    RED_ON = 0x11
    RED_OFF = 0x21
    RED_BLINK = 0x41

    YELLOW = 1
    YELLOW_ON= 0x12
    YELLOW_OFF = 0x22
    YELLOW_BLINK = 0x42

    GREEN = 2
    GREEN_ON = 0x14
    GREEN_OFF = 0x24
    GREEN_BLINK = 0x44

    BUZZER = 3
    BUZZER_ON = 0x18
    BUZZER_OFF = 0x28
    BUZZER_BLINK = 0x48

    def __init__(self):
        self.serialPort = '/dev/ttyUSB0'  # For the pi
        if sys.platform.startswith('darwin'): # MacOS has a different path
            self.serialPort = '/dev/tty.usbserial-210'  # For the mac

        self.baudRate = 9600
        self.state = [False, False, False, False] # [RED, YELLOW, GREEN, BUZZER]

        self.mSerial = None

        try:
            self.mSerial = serial.Serial(self.serialPort, self.baudRate)
            self.connected = True
        except:
            self.connected = False

    def sendCommand(self, cmd):
        if self.connected:
            self.mSerial.write(bytes([cmd]))

    def red(self, on):
        if self.connected:
            if on and not self.state[self.RED]: # Turn red on if it is currently off
                if self.state[self.YELLOW]: # Yellow is on so turn it off
                    self.yellow(False)
                if self.state[self.GREEN]: # Green is on so turn it off
                    self.green(False)
                if self.state[self.BUZZER]: # Buzzer is on so turn it off
                    self.buzzer(False)
            
                self.sendCommand(self.RED_ON)
                self.state[self.RED] = True
            elif not on and self.state[self.RED]: # Turn red off if it is currently on
                self.sendCommand(self.RED_OFF)
                self.state[self.RED] = False

    def yellow(self, on):
        if self.connected:
            if on and not self.state[self.YELLOW]: # Turn yellow on if it is currently off
                if self.state[self.RED]: # Red is on so turn it off
                    self.sendCommand(self.RED_OFF)
                if self.state[self.GREEN]: # Green is on so turn it off
                    self.green(False)
                if self.state[self.BUZZER]: # Buzzer is on so turn it off
                    self.buzzer(False)
            
                self.sendCommand(self.YELLOW_ON)
                self.state[self.YELLOW] = True
            elif not on and self.state[self.YELLOW]: # Turn yellow off if it is currently on
                self.sendCommand(self.YELLOW_OFF)
                self.state[self.YELLOW] = False
    
    def green(self, on):
        if self.connected:
            if on and not self.state[self.GREEN]: # Turn green on if it is currently off
                if self.state[self.RED]: # Red is on so turn it off
                    self.sendCommand(self.RED_OFF)
                if self.state[self.YELLOW]: # Yellow is on so turn it off
                    self.yellow(False)
                if self.state[self.BUZZER]: # Buzzer is on so turn it off
                    self.buzzer(False)
            
                self.sendCommand(self.GREEN_ON)
                self.state[self.GREEN] = True
            elif not on and self.state[self.GREEN]: # Turn green off if it is currently on
                self.sendCommand(self.GREEN_OFF)
                self.state[self.GREEN] = False

    def buzzer(self, on):
        if self.connected:
            if on and not self.state[self.BUZZER]: # Turn buzzer on if it is currently off
                if self.state[self.RED]: # Red is on so turn it off
                    self.sendCommand(self.RED_OFF)
                if self.state[self.YELLOW]: # Yellow is on so turn it off
                    self.yellow(False)
                if self.state[self.GREEN]: # Green is on so turn it off
                    self.green(False)
            
                self.sendCommand(self.BUZZER_ON)
                self.state[self.BUZZER] = True
            elif not on and self.state[self.BUZZER]: # Turn buzzer off if it is currently on
                self.sendCommand(self.BUZZER_OFF)
                self.state[self.BUZZER] = False

    def all_off(self):
        if self.connected:
            # Clean up any old state
            self.red(False)
            self.yellow(False)
            self.green(False)
            self.buzzer(False)

    def quit(self):
        self.all_off()
        self.mSerial.close()