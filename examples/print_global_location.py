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

# {marker_id: [x,y,z,angle],,,}
marker_map = {
    24836: [0, 0, 0, 0],
    25092: [1.5, 0, 0, 0],
    24594: [0, -1.5, 0, 0],
    24706: [1.5, -1.5, 0, 0]
}
sg = Stargazer(serial_device, marker_map)
while True:
    data = sg.fetch_data()
    if data.have_location_data:
        print("{:.3f}, {:.3f}, {:.3f}, marker:{}".format(data.x, data.y, data.z, data.marker_id))
