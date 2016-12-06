#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *
import numpy as np
import time
import re
import warnings

class StargazerData(object):
    """docstring for StargazerData"""

    def __init__(self, output_str, multi_id=True, marker_map=None):
        super(StargazerData, self).__init__()
        if not multi_id:
            raise StarGazerException("Single ID version is not implemented now. use legacy version.")

        if type(output_str) != str:
            raise StarGazerException("Invalid output_str type: " + str(type(output_str)))

        self.time = time.time()
        self.raw_string = output_str
        self.angle = self.x = self.y = self.z = None
        self.markers = None
        self.is_deadzone = False

        two_data_match = re.search(MESSAGE_UTIL.TWO_DATA_REGEX, output_str)
        one_data_match = re.search(MESSAGE_UTIL.ONE_DATA_REGEX, output_str)

        if two_data_match:
            data = two_data_match.groups()
            marker_id_1 = int(data[0])
            location_1 = [float(data[1]) * np.pi / 180] + [float(v)*0.01 for v in data[2:5]]
            marker_id_2 = int(data[5])
            location_2 = [float(data[6]) * np.pi / 180] + [float(v)*0.01 for v in data[7:10]]
        elif one_data_match:
            data = one_data_match.groups()
            marker_id_1 = int(data[0])
            location_1 = [float(data[1]) * np.pi / 180] + [float(v)*0.01 for v in one_data_match.groups()[2:5]]
            marker_id_2 = location_2 = None
        elif re.match(MESSAGE_UTIL.DEAD_ZONE_MESSAGE_REGEX, output_str):
            self.is_deadzone = True
            marker_id_1 = location_1 = marker_id_2 = location_2 = None
        else:
            warnings.warn('Invalid output string: ' + output_str)
            marker_id_1 = location_1 = marker_id_2 = location_2 = None

        try:
            abs_location_1 = marker_map[marker_id_1] + location_1
        except (KeyError, TypeError) as e:
            abs_location_1 = None
        try:
            abs_location_2 = marker_map[marker_id_2] + location_2
        except (KeyError, TypeError) as e:
            abs_location_2 = None

        if abs_location_1 is not None and abs_location_2 is not None:
            self.angle, self.x, self.y, self.z = ((abs_location_1 + abs_location_2)/2.).tolist()
            self.markers = [marker_id_1, marker_id_2]
        elif abs_location_1 is not None:
            self.angle, self.x, self.y, self.z = abs_location_1.tolist()
            self.markers = [marker_id_1]
        elif abs_location_2 is not None:
            self.angle, self.x, self.y, self.z = abs_location_2.tolist()
            self.markers = [marker_id_2]


    def __bool__(self):
        return (self.x is not None)
