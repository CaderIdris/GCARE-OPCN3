# GCARE OPC-N3 Monitor
#### Currently in Alpha
#### Joe Hayward (j.d.hayward@surrey.ac.uk)
#### COPYRIGHT 2021, Global Centre for Clean Air Research, The University of Surrey
#### GNU General Public License v3.0

__CAUTION: The run.sh script currently elevates main.py to have superuser permissions to fix a bug before immediate deployment. A later update will fix the bug and remove superuser permissions__

This program has been designed to be run on a Raspberry Pi running Ubuntu 20.04 LTS desktop 64 bit with an 800x640 touchscreen display. It is likely to run on other distributions and devices though some modifications may be required.

Adapted from Python2 code written by Daniel Jarvis and
licensed under GPL v3.0:
https://github.com/JarvisSan22/OPC-N3_python

---

## Table of Contents
1. [Standard Operating Procedure](#standard-operating-procedure)
2. [Settings](#settings)
3. [Setup](#setup)
4. [API](#api)
5. [Components](#components)

---

## Standard Operating Procedure

### Step 1: Run program

The GCARE-OPCN3 program can be run in one or two ways

#### Option A: Shortcut

If the __GCARE-extras.__ script was run during setup, an executable shortcut should be present on the desktop. Double click this to run the program.

![The Desktop](Images/SOP/01%20-%20Shortcut.png)

#### Option B: Terminal

The program can also be initialised via the terminal.
1. `cd ~/Documents/GCARE-OPCN3` (or whichever directory the repository has been saved in)
2. `bash run.sh` or `./run.sh`


![Running from Terminal](Images/SOP/01%20-%20Terminal.png)

Once the program is initialised via either method, the opening blurb should show, indicating some of the parameters used.

![Terminal Output](Images/SOP/02%20-%20Terminal%20running.png)

The first block shows the author information for the program, including current version number and status.

The second block shows where the data is being saved to. If no external devices are present like in this example, data is saved to the user's __Documents__ folder in the __OPC Data__ directory.

The third block indicates whether a connection to the device has been made. If it has not, the user may not have been properly added to the dialout group while running __setup.sh__ or the device may be connected to a different port to the one specified in __OPCSettings.json__.

The fourth block is the text output of the program testing the connection. You should be able to hear the fan being disabled and re-enabled. If you cannot, there may be an issue with the connection.

The fifth block indicates that the device is now recording measurements and informs the user on how and when to exit the program.

The sixth block indicates the time the measurement program started and when the first measurement will take place. More information on this can be found in [Settings](#settings).

While measuring, the program displays the latest measurement at the bottom of the terminal.

![Measurement Output](Images/SOP/03%20-%20Output.png)

---

## Settings

>To be added

---

## Setup

This setup section is assuming the program is to be run on __Ubuntu 20.04 LTS__ for __Raspberry Pi__. Other distributions and devices may vary.

### Step 1: Power on device
![The Home Screen](Images/Setup/01%20-%20Homescreen.png)

### Step 2: Ensure latest updates are installed
Ensure all packages on the device are up to date. Open the terminal via `CTRL + ALT + T` or via the home menu in the bottom left of the screen.

Enter `sudo apt update` to check whether any packages require updating. Enter the password when prompted.

![sudo apt update](Images/Setup/02%20-%20Update1.png)

If any packages need to be upgraded, enter `sudo apt upgrade`

![sudo apt upgrade](Images/Setup/02%20-%20Update2.png)

### Step 3: Download Program from GitHub
There are two ways to download the latest program from Github.

#### Option A: Download code from repository directly
Visit the repository at https://github.com/Joppleganger/GCARE-OPCN3 and open the green download menu located at the right side of the screen. Click download ZIP file to download an archive of the latest code which can then be extracted to a directory of your choice.

![Download from Github](Images/Setup/03%20-%20Download%20from%20Git.png)

#### Option B: Clone repository via git
If Git is installed on the system (`sudo apt install git`), the repository can be cloned directly from the github repository. Doing it this way means only a simple command needs to be run in order to install updates.
1. `cd ~/Documents` means any future commands will be executed in the user's Documents directory
2. `git clone https://github.com/Joppleganger/GCARE-OPCN3.git` clones the github repository to the user's documents folder

![Clone from Github](Images/Setup/03%20-%20Clone%20from%20Git%20A.png)

To update the repository, use the following code:

1. `cd ~/Documents/GCARE-OPCN3` means any future commands will be executed in the git repository
2. `git pull` updates any necessary files

![Update from Github](Images/Setup/03%20-%20Update%20from%20Git.png)

### Step 4: Run setup script
In order to setup the necessary components for the OPCN3 datalogger to run, the __setup.sh__ script has to be run.
1. `cd ~/Documents/GCARE-OPCN3` means any future commands will be executed in the git repository
2. `ls` lists all files in the directory, this allows you to check the setup file is present.
3. `bash setup.sh` or `./setup.sh` runs the setup script. The users password is required as some commands require to be run as the superuser.

It isn't advised to run unknown code with elevated permissions, so ensure you've read the contents of __setup.sh__ to ensure you know what it will do beforehand. This code is provided as is, without warranty of any kind, either express or implied. The setup script grants the user permission to access serial devices, in this case the OPC-N3, installs tools needed for Python3 and creates a Python3 virtual environment that contains the packages necessary for the program to operate.

![Run Setup Script](Images/Setup/04%20-%20Run%20Setup%20Script.png)

#### Optional Step 4A:
The repository also contains __GCARE-extras.sh__. This script is specifically for the GCARE use case though others may find it useful. It currently creates a shortcut on the desktop to __run.sh__, allowing the program to easily be initialised using a touchscreen.

1. `cd ~/Documents/GCARE-OPCN3` (or whichever directory the repository has been saved in)
2. `ls` lists all files in the directory, this allows you to check the GCARE-extras file is present.
3. `bash GCARE-extras.sh` or `./GCARE-extras.sh` runs the extras script. The users password is required as some commands required to be run as the superuser.

It isn't advised to run unknown code with elevated permissions, so ensure you've read the contents of __GCARE-extras.sh__ to ensure you know what it will do beforehand. This code is provided as is, without warranty of any kind, either express or implied.

![GCARE Extras](Images/Setup/04%20-%20GCARE%20Extras.png)

The program can then be initialised by double clicking the shortcut on the desktop.

![GCARE Extras](Images/Setup/04%20-%20Shortcut.png)

---

## API

>To be added

## Components

### Prototype

The prototypes of these sensors used the following components:
1. Raspberry Pi 4 Model B 4GB (Running Ubuntu Desktop 20.04 LTS 64 bit)
2. OKDO Raspberry Pi 3 7" Touchscreen Display (Compatible with RPi 4)
3. Alphasense OPC-N3
4. Alphasense USB-SPI Bridge
5. Verbatim 32 GB Micro SD Card
6. Verbatim 64 GB USB3 Memory Stick
