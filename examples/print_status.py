#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from pystargazer import *

serial_device = sys.argv[1]
map_file = sys.argv[2]
sg = StarGazer(serial_device, map_file)
print("# time angle x y z marker_id1 marker_id2")
while True:
    time, location, markers = sg.read_status()
    if location is None:
        print("# Dead zone.")
    else:
        #print(time, *(location+markers))
        print(location[3])
