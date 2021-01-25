#!/usr/bin/env bash
cd $(dirname $0)

PYTHON_VENV=OPCN3/bin/python3

$PYTHON_VENV main.py

read -p "Press Enter to close" reply
