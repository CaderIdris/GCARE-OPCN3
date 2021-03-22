#!/usr/bin/env bash


directory=$(pwd)
autorun_command="${directory}/autorun.sh"
sudo printf "\n${autorun_command}" >> ~/.profile
