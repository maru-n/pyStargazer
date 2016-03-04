#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *
import time

serial_device = sys.argv[1]
sg = Stargazer(serial_device, sys.argv[2])
while True:
    data = sg.fetch_data()
    print(data.raw_string)
    if data:
        print(data.angle, data.x, data.y, data.z)
