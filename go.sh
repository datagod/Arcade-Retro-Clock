#!/bin/bash
echo ""
echo ""
echo "--------------------------------------------------------"
ip addr
echo "--------------------------------------------------------"
echo ""
echo ""


IsRunning=$(ps -aux | grep -c '[A]rcadeRetroClock' )

echo "IsRunning: ${IsRunning}"

if [[ $IsRunning -gt "0" ]]; then
    echo ""
    echo "--------------------------------------------------------"
    echo "It seems that the clock is already running! Kill the existing process before running again: sudo kill `pidof -x $(basename $0) -o %PPID`"
    echo "--------------------------------------------------------"
    exit
fi



cd Clock
#CPU Modifier - used to regulate speed of certain games
# 1 = Raspberry Pi A
# 5 = Raspberry Pi 2

# STANDARD UNICORN
#mainsleep flashsleep scrollsleep mindots maxdots NightModeStart NightModeDuration(hours) CPUModifier
sudo python PacDot.py 0.07 0.07 0.07 20 55 23 7 1

# HD UNICORN
#mainsleep flashsleep scrollsleep NightModeStart NightModeDuration(hours) CPUModifier
#sudo python PacDotHD2.py 0.07 0.01 0.07 23 7 3
