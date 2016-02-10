#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *
import re
from threading import Thread, Event
import serial
import time
import re
import numpy as np
import warnings

DEBUG = False

STX = '~'  # start of text data
ETX = '`'  # end of text data

READ_COMMAND_PREFIX = '@'
WRITE_COMMAND_PREFIX = '#'
RETURN_VALUE_PREFIX = '$'
ACK_PREFIX = '!'
MESSAGE_PREFIX = '*'
VALUE_SEPARATER = '|'

# Message example:
# ~^124610|-3.70|+22.96|+98.73|216.09`
# ~^224610|-65.20|+22.18|+77.31|209.55|24594|-66.66|+22.79|-94.34|210.63`
DATA_REGEX = r'([0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([0-9]+\.?[0-9]+)'
ONE_DATA_REGEX = STX + r'\^1' + DATA_REGEX + ETX
TWO_DATA_REGEX = STX + r'\^2' + DATA_REGEX + r'\|' + DATA_REGEX + ETX

MAP_MODE_DATA_REGEX = r'~\^I([0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([0-9]+\.?[0-9]+)`'
DEAD_ZONE_MESSAGE_REGEX = r'~\*DeadZone`'


class StarGazer(object):
    """docstring for StarGazer"""

    def __init__(self, serial_device_name, map_file=None, multi_id=True):
        if not multi_id:
            raise StarGazerException("Single ID version is not implemented now. use legacy version.")
        super(StarGazer, self).__init__()
        self.__is_multi_id = multi_id
        self.__update_time = None
        self.__latest_markers = None
        self.__latest_output = None
        self.__latest_location = None  # [angle, x, y, z]
        self.__is_dead_zone = False

        self.__map = self.__parse_map_file(map_file)

        self.__serial = serial.Serial(serial_device_name,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=0)
        self.__update_event = Event()
        self.__serial_io_thread = Thread(target=self.__run_serial_io)
        self.__serial_io_thread.start()


    # blocking method
    def read_status(self):
        self.__wait_update()
        return self.get_latest_status()


    def get_latest_status(self):
        if self.__is_dead_zone:
            return "DeadZone"
        else:
            return self.__update_time, self.__latest_location, self.__latest_markers


    # blocking method
    def read_output(self):
        self.__wait_update()
        return self.get_latest_output()


    def get_latest_output(self):
        return self.__latest_output


    def __run_serial_io(self):
        while True:
            self.__update()


    def __update(self):
        self.__update_event.clear()
        line = self.__read_line(timeout=None)
        if line is None:
            return

        two_data_match = re.search(TWO_DATA_REGEX, line)
        one_data_match = re.search(ONE_DATA_REGEX, line)
        if two_data_match:
            marker_id_1 = int(two_data_match.groups()[0])
            location_1 = [float(v) for v in two_data_match.groups()[1:5]]
            marker_id_2 = int(two_data_match.groups()[5])
            location_2 = [float(v) for v in two_data_match.groups()[6:10]]
        elif one_data_match:
            marker_id_1 = int(one_data_match.groups()[0])
            location_1 = [float(v) for v in one_data_match.groups()[1:5]]
            marker_id_2 = location_2 = None
        elif re.match(DEAD_ZONE_MESSAGE_REGEX, line):
            marker_id_1 = location_1 = marker_id_2 = location_2 = None
        else:
            warnings.warn('Invalid response: ' + line)
            #raise Exception('Invalid response: ' + line)

        location, markers = self.__calc_location(marker_id_1, location_1, marker_id_2, location_2)
        update_time = time.time()
        self.__update_time, self.__latest_output, self.__latest_location, self.__latest_markers = update_time, line, location, markers

        self.__update_event.set()


    def __wait_update(self):
        self.__update_event.wait()


    def __calc_location(self, marker_id_1, location_1, marker_id_2, location_2):
        try:
            abs_location_1 = self.__map[marker_id_1] + location_1
        except KeyError as e:
            abs_location_1 = None
        try:
            abs_location_2 = self.__map[marker_id_2] + location_2
        except KeyError as e:
            abs_location_2 = None

        if abs_location_1 is None and abs_location_2 is None:
            location = None
            markers = None
        elif abs_location_1 is None:
            location = abs_location_2.tolist()
            markers = [marker_id_2]
        elif abs_location_2 is None:
            location = abs_location_1.tolist()
            markers = [marker_id_1]
        else:
            location = ((abs_location_1 + abs_location_2)/2.).tolist()
            markers = [marker_id_1, marker_id_2]

        return location, markers


    def __read_line(self, timeout=None):
        byte_data = b''
        etx_byte = bytes(ETX, 'ascii')
        start_time = time.time()
        while True:
            c = self.__serial.read(1)
            byte_data += c
            if c == etx_byte:
                break
            if (timeout != None) and (time.time()-start_time > timeout):
                break
        try:
            line = byte_data.decode()
            self.__print_debug("recv: "+line)
            return line
        except Exception as e:
            self.__print_debug(e)
            return None

    def __parse_map_file(self, map_file):
        m = {}
        if map_file is None:
            warnings.warn("Map file is not specified. Location data can not be calculate.")
            return m

        map_data = np.loadtxt(map_file, comments="#")
        for marker_id, angle, x, y, z in map_data:
            m[int(marker_id)] = np.array([float(angle), float(x), float(y), float(z)])
        return m


    def __print_debug(self, msg):
        if DEBUG:
            print('\033[94m [DEBUG] \033[0m', msg)
