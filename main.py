""" Simple one file Python module that interfaces with Alphasense
OPC-N3 devices connected to a linux machine as a serial device

Adapted from Python2 code written by Daniel Jarvis and
licensed under GPL v3.0:
https://github.com/JarvisSan22/OPC-N3_python
"""

__author__ = "Joe Hayward"
__copyright__ = "Copyright 2020, The University of Surrey"
__credits__ = ["Joe Hayward"]
__license__ = "GNU General Public License v3.0"
__version__ = "2021.1.4.1052"
__maintainer__ = "Joe Hayward"
__email__ = "j.d.hayward@surrey.ac.uk"
__status__ = "Production"

import datetime
import json
import time
from dataclasses import dataclass

import serial



def fancy_print(str_to_print, length=60, form='NORM', char='#'):
    """ Makes strings output to the console look nicer

    This function is used to make the console output of python
    scripts look nicer. This function is used in a range of
    modules to save time in formatting console output.

        Keyword arguments:
            str_to_print (str): The string to be formatted and printed

            length (int): Total length of formatted string

            form (str): String indicating how 'str_to_print' will be
            formatted. The options are:
                'TITLE': Centers 'str_to_print' and puts one char at
                         each end
                'NORM': Left justifies 'str_to_print' and puts one char
                        at each end (Norm doesn't have to be specified,
                        any option not listed here has the same result)
                'LINE': Prints a line of 'char's 'length' long

            char (str): The character to print.

        Variables:
            length_slope (float): Slope used to adjust length of line.
            Used if an emoji is used for 'char' as they take up twice
            as much space. If one is detected, the length is adjusted.

            length_offset (int): Offset used to adjust length of line.
            Used if an emoji is used for 'char' as they take up twice
            as much space. If one is detected, the length is adjusted.

        Returns:
            Nothing, prints a 'form' formatted 'str_to_print' of
            length 'length'
    """
    length_adjust = 1
    length_offset = 0
    if len(char) > 1:
        char = char[0]
    if len(char.encode('utf-8')) > 1:
        length_adjust = 0.5
        length_offset = 1
    if form == 'TITLE':
        print(f"{char} {str_to_print.center(length - 4, ' ')} {char}")
    elif form == 'LINE':
        print(char*int(((length) * length_adjust) + length_offset))
    else:
        print(f"{char} {str_to_print.ljust(length - 4, ' ')} {char}")

def convertRH(rawRH):
    """ Converts raw RH output of OPCN3 to a real value.

    The equation used is quoted in Alphasense Document 072-0503:
    Supplemental SPI information for the OPC-N3 (Issue 3).

    Keyword Arguments:
        rawRH (int): Combination of LSB 58 and MSB 59

    Returns:
        Converted real RH value

    Adapted from Python2 code written by Daniel Jarvis and
    licensed under GPL v3.0:
    https://github.com/JarvisSan22/OPC-N3_python
    """
    return 100 * (rawRH / (2 ** (16 - 1)))

def convertT(rawT):
    """ Converts raw T output of OPCN3 to a real value.

    The equation used is quoted in Alphasense Document 072-0503:
    Supplemental SPI information for the OPC-N3 (Issue 3).

    Keyword Arguments:
        rawT (int): Combination of LSB 56 and MSB 57

    Returns:
        Converted real RH value

    Adapted from Python2 code written by Daniel Jarvis and
    licensed under GPL v3.0:
    https://github.com/JarvisSan22/OPC-N3_python
    """
    return -45 + (175 * (rawT / (2 ** (16 - 1))))

def byteCombine(LSB, MSB):
    """ Combines Least Significant Byte and Most Significant Byte in to
    a 16 bit integer.

    Keyword Arguments:
        LSB (int): Least Significant byte
        MSB (int): Most Significant byte

    Returns:
        16 bit integer representing a combination of LSB and MSB

    Adapted from Python2 code written by Daniel Jarvis and
    licensed under GPL v3.0:
    https://github.com/JarvisSan22/OPC-N3_python
    """
    return (MSB << 8) | LSB

@dataclass
class SPIBytes:
    """ Dataclass containing bytes used to communicate with
    OPC-N3

    All bytecodes are taken from Alphasense Document 072-0503:
    Supplemental SPI information for the OPC-N3 (Issue 3).

        Attributes:
            adUSBAdapter (int): Address for the USB Adapter used with
                                the OPC-N3

            adOPC (int): Address for the OPC-N3

            pCommand (int): The command byte used to control OPC-N3
                            peripherals (the fan and laser)

            fanOff (int): The byte that follows 'pCommand' to disable
                          the fan

            fanOn (int): The byte that follows 'pCommand' to enable
                         the fan

            laserOff (int): The byte that follows 'pCommand' to disable
                            the laser

            laserOn (int): The byte that follows 'pCommand' to enable
                           the laser

            reqHist (int): The command byte used to request histogram
                           data

            reqData (int): The command byte used to request PM data.
                           This also resets the histogram.
    """
    adUSBAdapter: int = 0x5A  # Address the USB Adapter
    adOPC: int = 0x61  # Address the OPC
    pCommand: int = 0x03  # Command byte for peripherals (Fan/Laser)
    fanOff: int = 0x02
    fanOn: int = 0x03
    laserOff: int = 0x06
    laserOn: int = 0x07
    reqHist: int = 0x30
    reqData: int = 0x32

class OPC:
    """ Class that represents the connected OPC-N3

    Attributes:
        opc (serial object): The serial connection to the OPC-N3

        wait (float): The standard time to wait between messages

        isFanOn (boolean): True if fan should be on, false if not

        isLaserOn (boolean): True if laser should be on, false if not

    Methods:
        fanPower: Changes whether fan is on or off

        laserPower: Changes whether laser is on or off


    """
    def __init__(self, ser_conf):
        """ Initialises the class and initialises connection with OPC

            Keyword Arguments:
                ser_conf (dict): Contains all necessary information for
                                 pySerial3 to make a connection

            Adapted from Python2 code written by Daniel Jarvis and
            licensed under GPL v3.0:
            https://github.com/JarvisSan22/OPC-N3_python
        """
        self.opc = serial.Serial(**ser_conf)
        self.wait = 1e-06
        self.isFanOn = True
        self.isLaserOn = True

        # INITIALISE SPI CONNECTION
        time.sleep(1)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter,0x01]))
        self.opc.read(3)
        time.sleep(self.wait)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter,0x03]))
        self.opc.read(9)
        time.sleep(self.wait)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter,0x02,0x92,0x07]))
        self.opc.read(2)
        time.sleep(self.wait)

    def fanPower(self, status):
        """ Toggles OPC-N3 fan power status

            Keyword Arguments:
                status (boolean): True if fan is to be turned on, false
                                  if not

            Variables:
                loopCount (int): How many attempts have been made. If
                                 > 20, the SPI buffer is reset and
                                 loopCount is reset to 0

                fanStatus (int): The byte sent to the OPC to change
                                 the power status of the fan.
                                 fanOn is used to turn it on.
                                 fanOff is used to turn it off.

                opcReturn (int): Bytes returned by OPC to indicate
                                 whether it's ready to receive
                                 peripheral command or not

            Returns:
                Nothing, toggles the fan

            Adapted from Python2 code written by Daniel Jarvis and
            licensed under GPL v3.0:
            https://github.com/JarvisSan22/OPC-N3_python
        """
        loopCount = 0
        if status:  # True if fan is on, false if not
            fanStatus = SPIBytes.fanOn
        else:
            fanStatus = SPIBytes.fanOff
        while True:
            loopCount += 1
            self.opc.write(bytearray([SPIBytes.adOPC,SPIBytes.pCommand]))  # 0x03 is command byte
            opcReturn = self.opc.read(2)
            if opcReturn == (b"\xff\xf3" or b"xf3\xff"):
                time.sleep(self.wait)
                self.opc.write(bytearray([SPIBytes.adOPC, fanStatus]))
                self.opc.read(2)
                time.sleep(2)
                self.isFanOn = status
                break
            elif loopCount > 20:
                time.sleep(3)
                loopCount = 0
            else:
                time.sleep(self.wait * 10)

    def laserPower(self, status):
        """ Toggles OPC-N3 laser power status

            Keyword Arguments:
                status (boolean): True if laser is to be turned on, false
                                  if not

            Variables:
                loopCount (int): How many attempts have been made. If
                                 > 20, the SPI buffer is reset and
                                 loopCount is reset to 0

                laserStatus (int): The byte sent to the OPC to change
                                   the power status of the laser.
                                   laserOn is used to turn it on.
                                   laserOff is used to turn it off.

                opcReturn (int): Bytes returned by OPC to indicate
                                 whether it's ready to receive
                                 peripheral command or not

            Returns:
                Nothing, toggles the laser

            Adapted from Python2 code written by Daniel Jarvis and
            licensed under GPL v3.0:
            https://github.com/JarvisSan22/OPC-N3_python
        """
        loopCount = 0
        if status:  # True if fan is on, false if not
            laserStatus = SPIBytes.laserOn
        else:
            laserStatus = SPIBytes.laserOff
        while True:
            loopCount += 1
            self.opc.write(bytearray([SPIBytes.adOPC,SPIBytes.pCommand]))  # 0x03 is command byte
            opcReturn = self.opc.read(2)
            if opcReturn == (b"\xff\xf3" or b"xf3\xff"):
                time.sleep(self.wait)
                self.opc.write(bytearray([SPIBytes.adOPC, laserStatus]))
                self.opc.read(2)
                time.sleep(2)
                self.isLaserOn = status
                break
            elif loopCount > 20:
                time.sleep(3)
                loopCount = 0
            else:
                time.sleep(self.wait * 10)










if __name__ == "__main__":
    ### PROGRAM INIT
    FANCY_PRINT_CHARACTER = '\U0001F533'
    fancy_print('', form='LINE', char=FANCY_PRINT_CHARACTER)
    fancy_print('GCARE OPC-N3 Python Script', form='TITLE',
                char=FANCY_PRINT_CHARACTER)
    fancy_print(f'Author:  {__author__}', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'Contact: {__email__}', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'Version: {__version__}', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'Status:  {__status__}', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'License: {__license__}', char=FANCY_PRINT_CHARACTER)
    fancy_print('', form='LINE', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'- Connecting to OPC-N3', char=FANCY_PRINT_CHARACTER)

    ### LOAD OPC SETTINGS
    with open("OPCSettings.json", "r") as opc_config_json:
        opc_config = json.load(opc_config_json)
    serial_config = {
        "port": opc_config["Port"],
        "baudrate": 9600,
        "parity": serial.PARITY_NONE,
        "bytesize": serial.EIGHTBITS,
        "stopbits": serial.STOPBITS_ONE,
        "xonxoff": False,
        "timeout": 1
    }

    ### Initialise the OPC
    time.sleep(2)  # The OPC needs to boot
    opc = OPC(serial_config)
    fancy_print(f'- Connection Made', char=FANCY_PRINT_CHARACTER)
    fancy_print('', form='LINE', char=FANCY_PRINT_CHARACTER)

    ### Test the connection
    fancy_print(f'- Testing Connection', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'-- Disabling Fan', char=FANCY_PRINT_CHARACTER)
    opc.fanPower(False)
    fancy_print(f'-- Enabling Fan', char=FANCY_PRINT_CHARACTER)
    opc.fanPower(True)
    fancy_print(f'-- Disabling Laser', char=FANCY_PRINT_CHARACTER)
    opc.laserPower(False)
    fancy_print(f'-- Enabling Laser', char=FANCY_PRINT_CHARACTER)
    opc.laserPower(True)
    fancy_print('', form='LINE', char=FANCY_PRINT_CHARACTER)
