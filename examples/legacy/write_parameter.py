#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)

parameter = sys.argv[2]
value = sys.argv[3]

print(parameter, '=', value)

sg.calc_stop()
sg.write_parameter(parameter, value)
sg.save_settings()
sg.calc_start()
