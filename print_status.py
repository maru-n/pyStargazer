#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
print("# time Id, angle, x, y, x")
while True:
    data = sg.read_status()
    if data:
        mark_id, ang, x, y, z = data
        print(time.time(), mark_id, ang, x, y, z)
