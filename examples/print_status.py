#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
print("# angle x y z marker1 marker2")
while True:
    time, location, markers = sg.read_status()
    if location is None:
        print("Dead zone.")
    else:
        print(*location, end=" ")
        print(*markers)
