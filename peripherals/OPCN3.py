""" Module used to communicate with Alphasense OPC-N3 via USB-SPI
connection

This module contains classes and functions used to communicate with an
Alphasense OPC-N3 via USB-SPI connection, modify peripheral functions,
record data and format it so it can be saved to a csv file

    Classes:
        SPIBytes: Dataclass containing bytecodes that command the OPC
                  to perform various functions

        OPCN3: Represents an OPC-N3 connected via USB-SPI

    Functions:
        convert_RH: Converts raw RH output of OPCN3 to a real value

        convert_T: Converts raw T output of OPCN3 to a real value

        combine_bytes: Combines Least Significant Byte and Most
                       Significant Byte in to a 16 bit integer.

Some code in this module was adapted from Python 2 code written by
Daniel Jarvis and licensed under GPL v3.0.:
https://github.com/JarvisSan22/OPC-N3_python

Functions adapted from this code is marked in the docstrings.
"""

__author__ = "Idris Hayward"
__copyright__ = (
    "2020, Global Centre for Clean Air Research, " "The University of Surrey"
)
__credits__ = ["Idris Hayward"]
__license__ = "GNU General Public License v3.0"
__version__ = "2021.1.12.1822"
__maintainer__ = "Idris Hayward"
__email__ = "j.d.hayward@surrey.ac.uk"
__status__ = "Alpha"

from dataclasses import dataclass
from struct import unpack
import time

import serial


@dataclass
class SPIBytes:
    """Dataclass containing bytecodes that command the OPC to perform
    various functions

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
    fanSpeed: int = 0x42
    fanChannel: int = 0x00
    laserChannel: int = 0x01


class OPCN3:
    """Represents an OPC-N3 connected via USB-SPI

    Attributes:
        opc (serial object): The serial connection to the OPC-N3

        wait (float): The standard time to wait between messages

        isFanOn (boolean): True if fan should be on, false if not

        isLaserOn (boolean): True if laser should be on, false if not

        config (dict): User generated config file indicating operating
                       parameters of the instrument

        latestData (dict): Data output by OPC-N3, parsed by script.
                           Defaults to None if OPC does not send
                           data or data is not in expected format

    Methods:
        initConnection: Initalises connection with the OPC-N3

        fanPower: Changes whether fan is on or off

        laserPower: Changes whether laser is on or off

        getData: Requests histogram data from the OPC-N3 which also
                 resets the histogram after data is returned. The
                 data is then parsed and saved to latestData

        formatData: Formats data saved to latestData instance in to a
                    format suitable for writing to a csv file

        printOutput: Returns data stored in latestData in a format to
                     be printed
    """

    def __init__(self, serialConfig, deviceConfig):
        """Initialises the class

        Keyword Arguments:
            serialConfig (dict): Contains all necessary information
                                 for pySerial3 to make a connection

            deviceConfig (dict): User generated config file
                                 indicating operating parameters of
                                 the instrument

        Adapted from Python2 code written by Daniel Jarvis and
        licensed under GPL v3.0:
        https://github.com/JarvisSan22/OPC-N3_python
        """
        self.opc = serial.Serial(**serialConfig)
        self.wait = 1e-06
        self.isFanOn = True
        self.isLaserOn = True
        self.config = deviceConfig
        self.latestData = None

    def initConnection(self):
        """Initialises connection with the OPC-N3

        Returns:
            Nothing, initialises the connection with the OPC-N3


        Adapted from Python2 code written by Daniel Jarvis and
        licensed under GPL v3.0:
        https://github.com/JarvisSan22/OPC-N3_python
        """
        time.sleep(1)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter, 0x01]))
        self.opc.read(3)
        time.sleep(self.wait)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter, 0x03]))
        self.opc.read(9)
        time.sleep(self.wait)
        self.opc.write(bytearray([SPIBytes.adUSBAdapter, 0x02, 0x92, 0x07]))
        self.opc.read(2)
        time.sleep(self.wait)

    def fanPower(self, status):
        """Toggles OPC-N3 fan power status

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
            self.opc.write(
                bytearray([SPIBytes.adOPC, SPIBytes.pCommand])
            )  # 0x03 is command byte
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
        """Toggles OPC-N3 laser power status

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
            self.opc.write(
                bytearray([SPIBytes.adOPC, SPIBytes.pCommand])
            )  # 0x03 is command byte
            opcReturn = self.opc.read(2)
            if opcReturn == (b"\xff\xf3" or b"\xf3\xff"):
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

    def getData(self):
        """Requests histogram data from OPC-N3 and parses it

        Variables:
            loopCount (int): How many attempts have been made. If
                             > 20, the SPI buffer is reset and
                             loopCount is reset to 0

            opcReturn (int): Bytes returned by OPC to indicate
                             whether it's ready to receive
                             peripheral command or not

            opcHistBytesRaw (bytearray): Raw output of OPC-N3 when
                                         asked for data. The
                                         histogram data comprises
                                         of 86 bytes but 0x61 is
                                         also returned when each
                                         'any value' byte is sent
                                         so the byte array is 86*2
                                         bytes long

            opcHistBytes (list): opcHistBytesRaw with all useless
                                 0x61 values removes (all odd
                                 values removed)

            opcHistData (dict): Parsed data output by OPC-N3.
                                Contains optional "Bin Data"
                                subdict which contains all
                                histogram data, only stored if
                                requested in the instrument config

        Returns:
            Nothing, stores data in latestData attribute if
            successful, stores None in latestData if not

        Adapted from Python2 code written by Daniel Jarvis and
        licensed under GPL v3.0:
        https://github.com/JarvisSan22/OPC-N3_python
        """

        loopCount = 0
        while True:
            loopCount += 1
            self.opc.write(bytearray([SPIBytes.adOPC, SPIBytes.reqHist]))
            opcReturn = self.opc.read(2)
            if opcReturn == (b"\xff\xf3" or b"\xf3\xff"):
                # The OPC needs to return 86 bytes which it does in
                # exchange for 86 bytes of 'any value' (as stated in
                # supplemental SPI information). They then need to
                # be read from the SPI buffer
                for histByte in range(0, 86):
                    self.opc.write(bytearray([SPIBytes.adOPC, 0x45]))
                    time.sleep(self.wait)
                opcHistBytesRaw = bytearray(self.opc.read(size=172))
                # 86 bytes are expected. However, as the OPC also
                # returns xff when it receives the 'any value' byte,
                # the program reads 2 * 86 bytes
                opcHistBytes = [
                    histByte
                    for index, histByte in enumerate(opcHistBytesRaw)
                    if ((index + 1) % 2 == 0)
                ]
                if len(opcHistBytes) == 86:
                    opcHistData = {
                        "MToF (us)": round(
                            unpack("f", bytes(opcHistBytes[48:52]))[0] / 3, 3
                        ),
                        "Period (s)": combine_bytes(
                            opcHistBytes[52], opcHistBytes[53]
                        )
                        / 100,
                        "Flowrate (ml/s)": combine_bytes(
                            opcHistBytes[54], opcHistBytes[55]
                        )
                        / 100,
                        "Temp (C)": round(
                            convert_T(
                                combine_bytes(
                                    opcHistBytes[56], opcHistBytes[57]
                                )
                            ),
                            3,
                        ),
                        "RH (%)": round(
                            convert_RH(
                                combine_bytes(
                                    opcHistBytes[58], opcHistBytes[59]
                                )
                            ),
                            3,
                        ),
                        "PM1 (ug/m-3)": round(
                            unpack("f", bytes(opcHistBytes[60:64]))[0], 3
                        ),
                        "PM2.5 (ug/m-3)": round(
                            unpack("f", bytes(opcHistBytes[64:68]))[0], 3
                        ),
                        "PM10 (ug/m-3)": round(
                            unpack("f", bytes(opcHistBytes[68:72]))[0], 3
                        ),
                    }
                    if self.config["Use Bin Data"]:
                        opcHistData["Bin Data"] = dict()
                        for binNumber in range(0, 24):
                            opcHistData["Bin Data"][
                                f"Bin {binNumber + 1}"
                            ] = combine_bytes(
                                opcHistBytes[(binNumber * 2)],
                                opcHistBytes[(binNumber * 2) + 1],
                            )
                    self.latestData = opcHistData
                    break
                elif loopCount > 20:
                    time.sleep(3)  # Reset the SPI buffer
                    self.initConnection()  # Reinitialise connection
                    self.latestData = None
                    break
                else:
                    time.sleep(self.wait * 10)

    def formatData(self):
        """Formats data saved to latestData instance in to a format
        suitable for writing to a csv file.

        Formats headers and data in to formats suitable for writing to
        a csv file. Stores them in a dictionary file which splits up
        the measurement headers, data, bin headers and bin data. If
        no bin data is measured, the bin headers and bin data are
        saves as None values.

            Parameters:
                binKeys (list): Keys representing the different
                                particle size bins

                binHeaders (str): Headers for the bin data, suitable
                                  for a csv file

                binFormatted (str): Bin data, suitable for a csv file

                dataKeys (list): Keys representing all other
                                 measurements made by OPC

                dataHeaders (str): Headers for other measurements,
                                   suitable for a csv file

                dataFormatted (str): Other measurements, suitable for
                                     a csv file

            Returns:
                Dictionary with 4 keys {
                    "Headers": Headers for non bin measurements,
                    "Data": Non bin measurements,
                    "Bin Headers": Headers for bin measurements,
                    "Bin Data": Bin measurements
                }
                If no measurements are made, all are None
                If only non bin measurements are made, "Bin Headers"
                and "Bin Data" are None
        """
        if self.latestData is None:
            return {
                "Headers": None,
                "Data": None,
                "Bin Headers": None,
                "Bin Data": None,
            }
        if self.config["Use Bin Data"]:
            binKeys = list(self.latestData["Bin Data"].keys())
            binHeaders = ""
            binFormatted = ""
            for bIndex, binKey in enumerate(binKeys):
                if bIndex == 0:
                    binHeaders = f"{binKey}"  # f string to avoid
                    # unforseen behaviour
                    binFormatted = f"{self.latestData['Bin Data'][binKey]}"
                else:
                    binHeaders = f"{binHeaders}, {binKey}"
                    binFormatted = (
                        f"{binFormatted},"
                        f"{self.latestData['Bin Data'][binKey]}"
                    )
            self.latestData.pop("Bin Data", None)
        dataKeys = list(self.latestData.keys())
        dataHeaders = ""
        dataFormatted = ""
        for dataIndex, dataKey in enumerate(dataKeys):
            if dataIndex == 0:
                dataHeaders = f"{dataKey}"
                dataFormatted = f"{self.latestData[dataKey]}"
            else:
                dataHeaders = f"{dataHeaders}, {dataKey}"
                dataFormatted = f"{dataFormatted}, {self.latestData[dataKey]}"
        if self.config["Use Bin Data"]:
            return {
                "Headers": dataHeaders,
                "Data": dataFormatted,
                "Bin Headers": binHeaders,
                "Bin Data": binFormatted,
            }
        else:
            return {
                "Headers": dataHeaders,
                "Data": dataFormatted,
                "Bin Headers": None,
                "Bin Data": None,
            }

    def printOutput(self):
        """Returns data stored in latestData in a format to be printed

        Keyword Arguments:
            None

        Returns:
            If latestData contains measurements, returns a
            formatted string to be printed to the console. If
            latestData doesn't, a string of hashes is returned
            instead
        """
        if self.latestData is not None:
            return (
                f"PM1: {str(self.latestData['PM1 (ug/m-3)']).ljust(7)}| "
                f"PM2.5: {str(self.latestData['PM2.5 (ug/m-3)']).ljust(7)}| "
                f"PM10: {str(self.latestData['PM10 (ug/m-3)']).ljust(7)}"
            )
        else:
            return "#" * 38


def convert_RH(rawRH):
    """Converts raw RH output of OPCN3 to a real value

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
    return 100 * (rawRH / ((2 ** 16) - 1))


def convert_T(rawT):
    """Converts raw T output of OPCN3 to a real value.

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
    return -45 + (175 * (rawT / ((2 ** 16) - 1)))


def combine_bytes(LSB, MSB):
    """Combines Least Significant Byte and Most Significant Byte in to
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
