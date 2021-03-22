#!/usr/bin/env bash


directory=$(pwd)
autorun_command="${directory}/autorun.sh"
sudo printf "\nbash ${autorun_command}" >> ~/.profile
