#!/bin/bash

sudo usermod -a -G dialout $USERNAME
sudo apt install python3-pip
sudo apt install python3-venv
python3 -m venv "OPCN3"
source "OPCN3/bin/activate"
pip install -U setuptools pip
pip install pyserial
