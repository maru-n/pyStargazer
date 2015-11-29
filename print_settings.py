#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)

sg.calc_stop()

for p in PARAMETER:
    res = sg.read_parameter(p)
    print("%10s : %s"%(p.name, res))

sg.calc_start()
