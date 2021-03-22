#!/usr/bin/env bash


directory=$(pwd)
autorun_command="${directory}/autorun.sh"
grep "bash ${autorun_command}" || sudo printf "\nbash ${autorun_command}" >> ~/.profile
