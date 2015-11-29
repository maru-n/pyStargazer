#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from stargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)
sg.reset()
