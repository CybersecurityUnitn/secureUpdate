#!/usr/bin/env bash

cat $@ | grep WARNING
CHECK=$(cat $@ | grep "step\|assume")
[ -z "$CHECK" ] && echo "; WARNING: Empty proof"

/home/pi/Scaricati/deps/bin/ethos $@

