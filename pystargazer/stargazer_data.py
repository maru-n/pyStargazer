#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *
import numpy as np
import time
import re
import warnings


class LocationData(object):

    def __init__(self, marker_id=None, x=None, y=None, z=None, angle=None):
        super(LocationData, self).__init__()
        self.marker_id = marker_id
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

    @property
    def have_location_data(self):
        for i in [self.x, self.y, self.z, self.angle]:
            if i is None:
                return False
        return True

    def __array__(self):
        return np.array([self.x, self.y, self.z, self.angle])


class StargazerData(LocationData):

    def __init__(self, output_str, multi_id=True, marker_map=None):
        super(StargazerData, self).__init__()
        if not multi_id:
            raise StargazerException("Single ID version is not implemented now. use legacy version.")

        if type(output_str) != str:
            raise StargazerException("Invalid output_str type: " + str(type(output_str)))

        if not marker_map:
            marker_map = {}
        try:
            for i in marker_map:
                if len(marker_map[i]) != 3:
                    raise StargazerException("Invalid marker_map data on {} with {}".format(i, marker_map[i]))
        except Exception as e:
            raise StargazerException("Invalid marker_map data.")

        self.marker_id = []
        self.time = time.time()
        self.raw_string = output_str
        self.observed_markers = []
        self.local_location = []
        self.is_deadzone = False

        two_data_match = re.search(MESSAGE_UTIL.TWO_DATA_REGEX, output_str)
        one_data_match = re.search(MESSAGE_UTIL.ONE_DATA_REGEX, output_str)

        if two_data_match:
            data = two_data_match.groups()
            ld1 = LocationData(int(data[0]), float(data[2])*0.01, float(data[3])*0.01, -float(data[4])*0.01, float(data[1]) * np.pi / 180)
            ld2 = LocationData(int(data[5]), float(data[7])*0.01, float(data[8])*0.01, -float(data[9])*0.01, float(data[6]) * np.pi / 180)
            self.local_location.append(ld1)
            self.local_location.append(ld2)
            self.observed_markers.append(ld1.marker_id)
            self.observed_markers.append(ld2.marker_id)
        elif one_data_match:
            data = one_data_match.groups()
            ld = LocationData(int(data[0]), float(data[2])*0.01, float(data[3])*0.01, -float(data[4])*0.01, float(data[1]) * np.pi / 180)
            self.local_location.append(ld)
            self.observed_markers.append(ld.marker_id)
        elif re.match(MESSAGE_UTIL.DEAD_ZONE_MESSAGE_REGEX, output_str):
            self.is_deadzone = True
        else:
            warnings.warn('Invalid output string: ' + output_str, RuntimeWarning)

        dnum = 0
        for loc in self.local_location:
            mid = loc.marker_id
            if (marker_map is not None) and (mid in marker_map):
                if self.angle is None:
                    self.angle = self.x = self.y = self.z = 0.0
                self.marker_id.append(mid)
                abs_location = np.array(marker_map[mid]) + np.array(loc)[0:3]
                self.x += abs_location[0]
                self.y += abs_location[1]
                self.z += abs_location[2]
                self.angle += loc.angle
                dnum += 1

        if dnum != 0:
            self.angle /= dnum
            self.x /= dnum
            self.y /= dnum
            self.z /= dnum
