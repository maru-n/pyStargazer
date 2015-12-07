#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
print("# time Id, angle, x, y, x")
while True:
    try:
        data = sg.read_status(ignore_deadzone=False)
        print(time.time(), data[0], data[1], data[2], data[3], data[4])
    except DeadZoneException as e:
        print("#", time.time(), "DeadZone.")
