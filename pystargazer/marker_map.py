#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


class MarkerMap(object):
    """docstring for MarkerMap"""

    def __init__(self, marker_map_file):
        super(MarkerMap, self).__init__()
        self.__m = {}
        try:
            map_data = np.loadtxt(marker_map_file, comments="#", ndmin=2)
        except Exception as e:
            return

        for marker_id, angle, x, y, z in map_data:
            self.__m[int(marker_id)] = np.array([float(angle), float(x), float(y), float(z)])


    def get_location(self, marker_id):
        return self.__m[marker_id]


    def __bool__(self):
        return bool(self.__m)
