#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)

sg.calc_stop()

sg.write_parameter(PARAMETER.MarkType, 'HLD1L')
sg.write_parameter(PARAMETER.MarkMode, 'Alone')
sg.save_settings()

sg.calc_start()
