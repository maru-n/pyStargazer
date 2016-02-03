#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
print("# time marker_id, x, y, z, angle")
while True:
    data = sg.read_status()
    print(data)
