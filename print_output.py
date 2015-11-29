#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import stargazer

serial_device = sys.argv[1]
sg = stargazer.StarGazer(serial_device)
while True:
    line = sg.read_raw_output()
    print(line)
