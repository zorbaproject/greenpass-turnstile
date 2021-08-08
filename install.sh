#!/bin/bash

echo "This install script is intended for a RaspberryPi 3"

sudo apt-get update
sudo apt install aptitude tmux

sudo apt-get install pcscd libpcsclite1 pcsc-tools libccid libnss3-tools opensc-pkcs11
sudo apt-get install swig -y
sudo apt-get install python3-pyscard -y

sudo apt-get install python3-opencv python3-sip libjasper-dev libatlas-base-dev -y
sudo pip3 install opencv-contrib-python==4.1.0.25
sudo apt install libqtgui4 libqt4-test
sudo apt install python3-pil

sudo aptitude install python3-rpi.gpio
#sudo pip3 install w1thermsensor
sudo apt install python3-pip

#We need python2 for this due to conflicts on Debian
sudo apt-get install python-qrtools


#GUI libraries
sudo apt install libpyside2-dev pyside2-tools
sudo apt install python3-pyside2*
#Minimalistic option: sudo apt install python3-pyside2.qtgui python3-pyside2.qtcore python3-pyside2.qtconcurrent

#access serial ports (e.g.: /dev/ttyUSB0) as non root
sudo pip3 install pyserial
sudo usermod -a -G dialout $(whoami)

#needed to make a noise
sudo pip3 install beepy

#ehc requirements
scriptdir=$(dirname "$(readlink -f "$0")")
sudo pip3 install -r $scriptdir/verify-ehc/requirements.txt
sudo apt install python3-lxml

#Run autologin to make app run at boot
chmod +x autologin.sh
sudo ./autologin.sh


sudo apt clean

echo "Now just reboot the system and wait for the interface to load."
