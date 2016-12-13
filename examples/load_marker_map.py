#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import load_marker_map
from os import path

if len(sys.argv) != 2:
    print("Usage:")
    print("{} [fname]".format(path.basename(__file__)))
    sys.exit()

fname = sys.argv[1]
marker_map = load_marker_map(fname)
print(marker_map)
