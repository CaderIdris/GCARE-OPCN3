""" Interface with Alphasense OPC-N3 device connected to a linux
machine as a serial device and saves measurements in csv file

This program interfaces with an Alphasense OPC-N3 via a USB-SPI
interface. It was designed with a Raspberry Pi or other similar SBC.
It prefers to store data to an external device mounted in the media
folder, then the mnt folder. If there is no device mounted in either,
or more than one, it saves data in the documents folder of the user
running the script. The filepath can be overwritten in OPCSettings.json
which controls several different operating parameters.
The measurements made by the OPC-N3 are returned from the OPC-N3 module
located in peripherals/ and saved to a csv file located in the
filepath. If this file doesn't exist, it is made.

    Command Line Arguments:
        None

    Parameters:
        timeDifference (int): Time in seconds between measurements

        fancyPrintCharacter (char): Single character that's used for
                                      the fancy_print function

        opcConfig (dict): Config options parsed from OPCSettings.json
                          Contains the following keys:
                            "Name" (str): Name of the Sensor
                            "Port" (str): Path to the SPI interface
                            "Use Bin Data" (boolean): Save bin data
                                                      to spreadsheet?
                            "Fan Speed" (int): Digital pot setting
                                               for fan (currently
                                               unused)

        serialConfig (dict): Config options for serial device. Should
                             not need altering for the OPC-N3

        opc (OPC-N3 Class): Class object representing an instance of
                            the OPC-N3

        firstMeasurementTime (datetime): When the first measurement
                                         will take place

        startTime (float): When the measurement starts, expressed in
                           seconds since epoch and calculated with
                           time.time()

    Functions:
        fancy_print: Makes string output to console look nicer

        find_valid_path: Finds and returns a valid path to save data to

        save_to_file: Saved recorded data to OPC Data directory,
                      creating a file with appropriate headers if one
                      doesn't exist

        bin_Nones: One line function to return blank measurements for
                   the bin values
"""

__author__ = "Joe Hayward"
__copyright__ = "2020, Global Centre for Clean Air Research, "\
                "The University of Surrey"
__credits__ = ["Joe Hayward"]
__license__ = "GNU General Public License v3.0"
__version__ = "2021.1.14.1318"
__maintainer__ = "Joe Hayward"
__email__ = "j.d.hayward@surrey.ac.uk"
__status__ = "Beta"

import datetime as dt
import json
import time
import os
import getpass
import warnings

import serial

from peripherals.OPCN3 import OPCN3 as OPC

fancyPrintCharacter = '\U0001F533'


def fancy_print(str_to_print, length=70, form='NORM', char='#'):
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


def find_valid_path():
    """ Finds and returns a valid path to save data to

    If a path isn't declared, this program attempts to find one. First,
    it looks for any external devices located in the media directory.
    If it can't find any there, it looks for any external devices in
    the mnt directory. If it can't find any there, it saves to the
    users documents directory. The rational behind the order of this is
    that the Raspberry Pis should prefer saving to an external device
    to the SD card as an external drive is less likely to corrupt if
    the Raspberry Pi loses power, therefore making them a better
    option. External devices located in the media folder are scanned
    first as it's unlikely that any will be permanently mounted for our
    specific needs, other people's requirements will undoubtedly vary.
    The Documents folder is chosen last as it should exist in nearly
    all use cases as a backup, though storing to the SD card is not
    ideal as discussed earlier.

        Keyword Arguments:
            None

        Variables:
            media_dirs (list): List of tuples containing info on the
                               directories located in /media/"usr"/
                               where usr is the current accounts
                               username, called via getpass.getuser()

            mnt_dirs (list): List of tuples containing info on the
                             directories located in /mnt/

        Returns:
            IF 1 directory present in media, it returns the path to
            that external device
            ELIF 1 directory present in mnt, it returns the path tp
            that external device
            ELSE it returns the path to the Documents directory,
            calculated via the relative path by os.path.expanduser()
            The OPCData directory is added to these paths
    """
    try:
        media_dirs = [f.path for f in os.scandir(f"/media/{getpass.getuser()}/")
                        if f.is_dir()]
        if len(media_dirs) == 1:
            return f"{media_dirs[0]}/OPC Data/"
        elif len(media_dirs) > 1:
            fancy_print(f"{len(media_dirs)} external devices found in " \
                f"/media/{getpass.getuser()}/. Unmount {len(media_dirs) - 1} " \
                f"devices or give file path", char=fancyPrintCharacter)
        else:
            fancy_print(f"No external devices found in /media/{getpass.getuser()}/",
                char=fancyPrintCharacter)
    except FileNotFoundError:
        fancy_print(f"No external devices found in /media/{getpass.getuser()}/",
            char=fancyPrintCharacter)
    try:
        mnt_dirs = [f.path for f in os.scandir("/mnt") if f.is_dir()]
        if len(mnt_dirs) == 1:
            return f"{mnt_dirs[0]}/OPC Data/"
        elif len(mnt_dirs) > 1:
            fancy_print(f"{len(mnt_dirs)} found in /mnt/." \
                f" Unmount {len(mnt_dirs) - 1} devices or give file path",
                char=fancyPrintCharacter)
        else:
            fancy_print(f"No external devices found in /mnt/",
                char=fancyPrintCharacter)
    except FileNotFoundError:
        fancy_print(f"No external devices found in /mnt/",
            char=fancyPrintCharacter)
    return os.path.expanduser("~/Documents/OPC Data/")


def first_measurement_time(timeInterval, currentTime):
    """ Works out when the first measurement should take place

    The first measurement is synced up so measurements will always
    fall on the start of every hour and increase in intervals set in
    OPCSettings.json. This function ensures the first measurement is
    made at the interval closest to when the program is initialised.

        Keyword Arguments:
            timeInterval (str): The interval between measurements set
                                in OPCSettings.json. If an incorrect
                                value is set, the program warns the
                                user and defaults to 1m

            currentTime (datetime): The time the last measurement took
                                    place

        Parameters:
            validMinutes (list of int): The minutes that measurements
                                        will be made on

            currentMinute (int): The minute the program was initialised
                                 on

            nextMinute (int): The first minute a measurement will occur

            nextMeasurement (datetime): When the first measurement will
                                        occur

        Returns:
            nextMeasurement
    """
    setIntervals = {
        '1m': 1,
        '5m': 5,
        '10m': 10,
        '15m': 15,
        '30m': 30,
        '1h': 60
    }
    if timeInterval not in list(setIntervals.keys()):
        warnings.warn("Specified time interval not expected, defaulting to" \
                      " 1m")
        timeInterval = '1m'
    validMinutes = list(range(0, 60, setIntervals[timeInterval]))

    currentMinute = int(currentTime.strftime("%M"))
    nextMinute = 60
    for index, minute in enumerate(validMinutes[1:]):
        if minute > currentMinute:
            nextMinute = minute
            break
    if nextMinute < 60:
        nextMeasurement = currentTime.replace(minute=nextMinute, second=0,
            microsecond=0)
    else:
        nextMeasurement = currentTime.replace(minute=0, second=0,
            microsecond=0) + dt.timedelta(hours=1)
    return nextMeasurement


def next_measurement_time(timeInterval, currentTime):
    """ Calculates when the next measurement is

        Keyword Arguments:
            timeInterval (str): The interval between measurements set
                                in OPCSettings.json. If an incorrect
                                value is set, the program warns the
                                user and defaults to 1m

            currentTime (datetime): The time the last measurement took
                                    place

        Parameters:
            setIntervals (dict): The number of minutes between set time
                                 intervals. This should be moved to a
                                 json later on for easier customisation

            nextTime (datetime): When the next measurement will take
                                 place

        Returns:
            nextTime with second and microsecond set to 0
    """
    setIntervals = {
        '1m': 1,
        '5m': 5,
        '10m': 10,
        '15m': 15,
        '30m': 30,
        '1h': 60
    }
    if timeInterval not in list(setIntervals.keys()):
        timeInterval = '1m'
    nextTime = currentTime + dt.timedelta(minutes=setIntervals[timeInterval])
    return nextTime.replace(second=0, microsecond=0)


def save_to_file(opcData, timestamp, filePath):
    """ Saved recorded data to OPC Data directory, creating a file with
    appropriate headers if one doesn't exist

    The formatted data measured by the OPC is saved to a csv file.
    If there is bin data in the formatted data and expected by the file
    it is recorded.
    If there is bin data in the formatted data but not expected by the
    file it is discarded.
    If there isn't bin data in the formatted data but it expected by
    the file then the bin data columns are populated with None values
    If the file isn't in the directory it is created, if bin data is
    present then bin data headers are added, otherwise the file does
    not expect bin data.

        Keyword Arguments:
            opcData (dict): Measurements made by the OPC formatted by
                            the formatData method. Contains 4 keys,
                            Headers, Data, Bin Headers, Bin Data.
                            Each key contains a preformatted string
                            to be saved to the csv file

            timestamp (datetime): The time the measurement was made

            filePath (str): Path to save the file to

        Variables:
            fileName (str): What file to save it to, determined by the
                            measurement date (YYYY-MM-DD)

            measurementTime (str): When the measurement was made,
                                   second resolution
                                   (YYYY-MM-DD HH:MM:SS)

            fileHeaders (str): Headers already present in file if file
                               is present or headers to be added to
                               file if it is being created


            csvFile (File): Object representing the csv file that data
                            if being appended to

            binHeadersPresent (boolean): Are there headers containing
                                         the phrase "Bin" present in
                                         the file headers?

            binDataPresent (boolean): Is there bin data present in the
                                      formatted measurements made by
                                      the OPC?

            firstMeasurements (str): The first measurements to be
                                     appended to the csv file
    """
    fileName = f'{filePath}{timestamp.strftime("%Y-%m-%d")}.csv'
    measurementTime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(fileName, "r+") as csvFile:
            fileHeaders = csvFile.readline()
            binHeadersPresent = ("Bin" in fileHeaders)
            binDataPresent = opcData["Bin Headers"] is not None
            csvFile.read()
            if binHeadersPresent and binDataPresent:
                # If there's bin headers and bin data, go for it!
                csvFile.write(f'{measurementTime}, {opcData["Data"]}, ' \
                    f'{opcData["Bin Data"]}\n')
            elif binHeadersPresent:
                # If there's bin headers and no bin data, log None
                csvFile.write(f'{measurementTime}, {opcData["Data"]}, ' \
                    f'{bin_Nones()}\n')
            else:
                # If there's bin data but no bin headers, or no bin
                # data and no bin headers, don't log it
                csvFile.write(f'{measurementTime}, {opcData["Data"]}\n')
    except FileNotFoundError:
        fileHeaders = None
        firstMeasurements = None
        if opcData["Bin Headers"] is not None:
            fileHeaders = f'Timestamp, {opcData["Headers"]}, ' \
                f'{opcData["Bin Headers"]}'
            firstMeasurements = f'{measurementTime}, {opcData["Data"]}, ' \
                f'{opcData["Bin Data"]}'
        elif opcData["Headers"] is not None:
            fileHeaders = f'Timestamp, {opcData["Headers"]}'
            firstMeasurements = f'{measurementTime}, {opcData["Data"]}'
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        if (fileHeaders and firstMeasurements) is not None:
            with open(fileName, "w") as csvFile:
                csvFile.write(f'{fileHeaders}\n')
                csvFile.write(f'{firstMeasurements}\n')


def bin_Nones():
    """ One line function to return blank measurements for the bin
    values

        Keyword Arguments:
            None

        Returns:
            24 comma delimited None values for csv file
    """
    return ('None, ' * 23) + 'None'



if __name__ == "__main__":
    ### PROGRAM INIT
    fancy_print('', form='LINE', char=fancyPrintCharacter)
    fancy_print('GCARE OPC-N3 Python Script', form='TITLE',
        char=fancyPrintCharacter)
    fancy_print(f'Author:  {__author__}', char=fancyPrintCharacter)
    fancy_print(f'Contact: {__email__}', char=fancyPrintCharacter)
    fancy_print(f'Version: {__version__}', char=fancyPrintCharacter)
    fancy_print(f'Status:  {__status__}', char=fancyPrintCharacter)
    fancy_print(f'License: {__license__}', char=fancyPrintCharacter)
    fancy_print('', form='LINE', char=fancyPrintCharacter)

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
    timeDifference = opcConfig["Measurement Time"]
    if opcConfig["File Path"] == "":
        opcConfig["File Path"] = find_valid_path()
    if not os.path.isdir(opcConfig["File Path"]):
        os.makedirs(opcConfig["File Path"])
    fancy_print(f'- Saving data to{opcConfig["File Path"]}',
    char=fancyPrintCharacter)
    fancy_print('', form='LINE', char=fancyPrintCharacter)
    fancy_print('Connecting to OPC-N3', char=fancyPrintCharacter)

    ### Initialise the OPC
    time.sleep(2)  # The OPC needs to boot
    opc = OPC(serialConfig, opcConfig)
    opc.initConnection()
    fancy_print('- Connection Made', char=fancyPrintCharacter)
    fancy_print('', form='LINE', char=fancyPrintCharacter)

    ### Test the connection
    fancy_print('Testing Connection', char=fancyPrintCharacter)
    fancy_print('- Disabling Fan', char=fancyPrintCharacter)
    opc.fanPower(False)
    fancy_print('- Enabling Fan', char=fancyPrintCharacter)
    opc.fanPower(True)
    fancy_print('- Disabling Laser', char=fancyPrintCharacter)
    opc.laserPower(False)
    fancy_print('- Enabling Laser', char=fancyPrintCharacter)
    opc.laserPower(True)
    fancy_print('', form='LINE', char=fancyPrintCharacter)

    ### Record data
    fancy_print(f'Recording measurements', char=fancyPrintCharacter)
    fancy_print(f'- Exit via CTRL-C or by closing the terminal',
        char=fancyPrintCharacter)
    fancy_print(f'-- Do not exit if "Storing Data" is displayed',
        char=fancyPrintCharacter)
    fancy_print(f'-- This could corrupt the file being written to',
        char=fancyPrintCharacter)
    fancy_print('', form='LINE', char=fancyPrintCharacter)
    nextMeasurementTime = first_measurement_time(timeDifference,
        dt.datetime.now())
    fancy_print(f'Current time is {dt.datetime.now().strftime("%H:%M:%S")}',
        char=fancyPrintCharacter)
    fancy_print(f'- Next measurement will be at ' \
                f'{nextMeasurementTime.strftime("%H:%M:%S")}',
        char=fancyPrintCharacter)
    fancy_print('', form='LINE', char=fancyPrintCharacter)
    print()
    time.sleep((nextMeasurementTime - dt.datetime.now()).seconds + 1)
    # 1 second added on otherwise it would start on the 59th second of
    # the previous minute, the joys of timedelta calculations
    while True:
        startTime = dt.datetime.now()
        print('Measuring data'.ljust(70), end="\r", flush=True)
        opc.getData()
        print('Storing Data'.ljust(70), end="\r", flush=True)
        save_to_file(opc.formatData(), dt.datetime.now(),
            opcConfig["File Path"])
        nextMeasurementTime = next_measurement_time(timeDifference,
            startTime)
        print(f'{opc.printOutput()} | Next Measurement: ' \
              f'{nextMeasurementTime.strftime("%H:%M:%S")}'.ljust(70),
              end="\r", flush=True)
        timeToNextMeasurement = nextMeasurementTime - dt.datetime.now()
        time.sleep((timeToNextMeasurement.microseconds) * 1e-6 +
                   timeToNextMeasurement.seconds)

        # 1 second added on otherwise it would start on the 59th second of
        # the previous minute, the joys of timedelta calculations
