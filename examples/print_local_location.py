#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import Stargazer
import numpy as np
from os import path

if len(sys.argv) != 2:
    print("Usage:")
    print("{} [device]".format(path.basename(__file__)))
    sys.exit()

serial_device = sys.argv[1]

sg = Stargazer(serial_device)
while True:
    data = sg.fetch_data()
    for d in data.local_location:
        print("{}=>({:.3f},{:.3f},{:.3f},{:.3f})  ".format(d.marker_id, d.x, d.y, d.z, d.angle), end="")
    print()
