""" Interface with Alphasense OPC-N3 device connected to a linux
machine as a serial device

    Command Line Arguments:
        None, currently

    Parameters:
        timeDifference (int): Time in seconds between measurements

        FANCY_PRINT_CHARACTER (char): Single character that's used for
                                      the fancy_print function

        opcConfig (dict): Config options parsed from OPCSettings.json
                          Contains the following keys:
                            "Name" (str): Name of the Sensor
                            "Port" (str): Path to the SPI interface                                on the computer
                            "Use Bin Data" (boolean): Save bin data
                                                      to spreadsheet?
                            "Fan Speed" (int): Digital pot setting
                                               for fan (currently
                                               unused)

        serialConfig (dict): Config options for serial device. Should
                             not need altering for the OPC-N3

        opc (OPC-N3 Class): Class object representing an instance of
                            the OPC-N3

        startTime (float): When the measurement starts, expressed in
                           seconds since epoch

        endTime (float): When the measurement ends, expressed in
                         seconds since epoch

Adapted from Python2 code written by Daniel Jarvis and
licensed under GPL v3.0:
https://github.com/JarvisSan22/OPC-N3_python
"""

__author__ = "Joe Hayward"
__copyright__ = "Copyright 2020, Global Centre for Clean Air Research, "\
                "The University of Surrey"
__credits__ = ["Joe Hayward"]
__license__ = "GNU General Public License v3.0"
__version__ = "2021.1.11.1907"
__maintainer__ = "Joe Hayward"
__email__ = "j.d.hayward@surrey.ac.uk"
__status__ = "Indev"

import datetime
import json
import time

import serial

from peripherals.OPCN3 import OPCN3 as OPC

def fancy_print(str_to_print, length=100, form='NORM', char='#'):
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


timeDifference = 60
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
    fancy_print(f'Copyright: {__copyright__}', char=FANCY_PRINT_CHARACTER)
    fancy_print('', form='LINE', char=FANCY_PRINT_CHARACTER)
    fancy_print(f'- Connecting to OPC-N3', char=FANCY_PRINT_CHARACTER)

    ### LOAD OPC SETTINGS
    with open("OPCSettings.json", "r") as opcConfigJson:
        opcConfig = json.load(opcConfigJson)
    serialConfig = {
        "port": opcConfig["Port"],
        "baudrate": 9600,
        "parity": serial.PARITY_NONE,
        "bytesize": serial.EIGHTBITS,
        "stopbits": serial.STOPBITS_ONE,
        "xonxoff": False,
        "timeout": 1
    }

    ### Initialise the OPC
    time.sleep(2)  # The OPC needs to boot
    opc = OPC(serialConfig, opcConfig)
    opc.initConnection()
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
    while True:
        startTime = time.time()
        opc.getData()
        endTime = time.time()
        print(opc.latestData)
        time.sleep(timeDifference - (endTime - startTime))
