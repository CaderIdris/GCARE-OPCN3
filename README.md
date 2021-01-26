# GCARE OPC-N3 Monitor
#### Currently in Alpha
#### Joe Hayward (j.d.hayward@surrey.ac.uk)
#### COPYRIGHT 2021, Global Centre for Clean Air Research, The University of Surrey
#### GNU General Public License v3.0

Adapted from Python2 code written by Daniel Jarvis and
licensed under GPL v3.0:
https://github.com/JarvisSan22/OPC-N3_python

---

## Table of Contents
1. [Standard Operating Procedure](#standard-operating-procedure)
2. [Settings](#program-settings)
3. [Setup](#setup)
4. [API](#api)

---

## Standard Operating Procedure

>To be added

---

## Program settings

>To be added

---

## Setup

This setup section is assuming the program is being run on Ubuntu 20.04 LTS for Raspberry Pi. Other distributions and devices may vary slightly. This guide assumes Ubuntu 20.04 LTS has already been installed on the Raspberry Pi.

### Step 1: Power on device
![The Home Screen](Images/Setup/01%20-%20Homescreen.png)

### Step 2: Ensure latest updates are installed
Ensure all packages on the Raspberry Pi are up to date. Open the terminal via `CTRL + ALT + T` or via the home menu in the bottom left of the screen.

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
In order to setup the necessary components for the OPCN3 datalogger to run, the setup script has to be run.
1. `cd ~/Documents/GCARE-OPCN3` means any future commands will be executed in the git repository
2. `ls` lists all files in the directory, this allows you to check the setup file is present.
3. `bash setup.sh` runs the setup script. The users password is required as some commands require to be run as the superuser.

It isn't advised to run unknown code with elevated permissions, so ensure you've read the contents of __setup.sh__ to ensure you know what it will do beforehand. This code is provided as is, without warranty of any kind, either express or implied. The setup script grants the user permission to access serial devices, in this case the OPC-N3, installs tools needed for Python3 and creates a Python3 virtual environment that contains the packages necessary for the program to operate.

![Run Setup Script](Images/Setup/04%20-%20Run%20Setup%20Script.png)

#### Optional Step 4A:
The repository also contains __GCARE-extras.sh__. This script is specifically for the GCARE use case though others may find it useful. It currently creates a shortcut on the desktop to __run.sh__, allowing the program to easily be initialised using a touchscreen.

![GCARE Extras](Images/Setup/04%20-%20GCARE%20Extras.png)

The program can then be initialised by double clicking the shortcut on the desktop


![GCARE Extras](Images/Setup/04%20-%20Shortcut.png)

---

## API

>To be added
