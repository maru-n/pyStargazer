#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *
from .stargazer_data import *
from .marker_map import *
from threading import Thread, Event
import serial
import time
import warnings


class Stargazer(object):
    """docstring for Stargazer"""

    DEBUG = False

    def __init__(self, serial_device_name, marker_map_file=None, multi_id=True):
        if not multi_id:
            raise StargazerException("Single ID version is not implemented now. use legacy version.")
        super(Stargazer, self).__init__()
        self.__is_multi_id = multi_id
        self.__latest_data = None
        self.__marker_map = MarkerMap(marker_map_file)
        if not self.__marker_map:
            warnings.warn("Marker map file is not specified or invalid. Location data will not be calculated.")
        self.__serial = serial.Serial(serial_device_name,
                                      baudrate=115200,
                                      bytesize=serial.EIGHTBITS,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE,
                                      timeout=0)
        self.__update_event = Event()
        self.__serial_io_thread = Thread(target=self.__run_serial_io)
        self.__serial_io_thread.daemon = True
        self.__serial_io_thread.start()


    # blocking method
    def fetch_data(self):
        self.__wait_update()
        return self.get_latest_data()


    def get_latest_data(self):
        return self.__latest_data


    def __run_serial_io(self):
        while True:
            self.__update()


    def __update(self):
        self.__update_event.clear()
        line = self.__read_line(timeout=None)
        if line is None:
            return
        self.__latest_data = StargazerData(line, marker_map=self.__marker_map)
        self.__update_event.set()


    def __wait_update(self):
        self.__update_event.wait()


    def __read_line(self, timeout=None):
        byte_data = b''
        etx_byte = bytes(MESSAGE_UTIL.ETX, 'ascii')
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


    def __print_debug(self, msg):
        if Stargazer.DEBUG:
            print('\033[94m [DEBUG] \033[0m', msg)
