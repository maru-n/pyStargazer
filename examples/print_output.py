#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *
import time

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
while True:
    output = sg.read_output()
    print(output)
