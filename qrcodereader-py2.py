#!/usr/bin/python
import sys

myfile = "green_pass.png"
if len(sys.argv) > 1:
    myfile = sys.argv[1]

from qrtools import QR
myQR = QR(filename = myfile)
myQR.decode()
print myQR.data
