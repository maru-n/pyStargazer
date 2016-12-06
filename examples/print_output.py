#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
from pystargazer import Stargazer


if len(sys.argv) != 2:
    print("Usage:")
    print("{} [device]".format(path.basename(__file__)))
    sys.exit()

serial_device = sys.argv[1]
sg = Stargazer(serial_device)
while True:
    data = sg.fetch_data()
    print(data.raw_string)
