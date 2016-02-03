#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *
import re
from threading import Thread, Event
import serial
import time
import re

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
TWO_DATA_REGEX = STX + r'\^2' + DATA_REGEX + VALUE_SEPARATER + ETX

MAP_MODE_DATA_REGEX = r'~\^I([0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([0-9]+\.?[0-9]+)`'
DEAD_ZONE_MESSAGE_REGEX = r'~\*DeadZone`'
MAP_ID_MESSAGE_REGEX = r'~\*MAPID\|([0-9]+)`'
MAP_DATA_SAVE_REGEX = r'~\!MapDataSave`'
PARAMETER_UPDATE_REGEX = r'~\!ParameterUpdate`'

_SEND_CHARACTER_INTERVAL = 0.01
_CHECK_ACK_WAIT_TIME = 1.0
_READ_RESPONSE_WAIT_TIME = 1.0
_PARAMETER_UPDATE_WAIT_TIME = 50.0

class StarGazer(object):
    """docstring for StarGazer"""

    def __init__(self, serial_device_name, map_coordinate_file=None, multi_id=True):
        if not multi_id:
            print("Single ID version is not implemented now. use legacy version.")
        super(StarGazer, self).__init__()
        self.__is_multi_id = multi_id
        self.__latest_output = None
        self.serial = serial.Serial(serial_device_name,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=0)
        self.update_event = Event()
        self.serial_io_thread = Thread(target=self.__run_serial_io)
        self.serial_io_thread.start()


    # blocking method
    def read_status(self):
        return None


    def get_latest_status(self):
        return this.current_status


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
        self.update_event.clear()
        line = self.__read_line(timeout=None)
        if line is not None:
            self.__latest_output = line;
        self.update_event.set()


    def __wait_update(self):
        self.update_event.wait()


    def __read_line(self, timeout=None):
        byte_data = b''
        etx_byte = bytes(ETX, 'ascii')
        start_time = time.time()
        while True:
            c = self.serial.read(1)
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
        if DEBUG:
            print('\033[94m [DEBUG] \033[0m', msg)




    #====================
    # Legacy code
    #====================
class StarGazerLegacy(object):
    def __init__(self, serial_device_name):
        super(StarGazer, self).__init__()
        self.sm = serial_manager.SerialManager(serial_device_name)
        self.is_building_map = None
        self.find_map_id = None


    def read_raw_output(self, timeout=None):
        output = self.sm.read_line(timeout = timeout)
        return output

    def read_status(self, timeout=None, ignore_deadzone=False):
        res, data, is_deadzone = self.sm.read_data(timeout=timeout, ignore_deadzone=ignore_deadzone)
        if is_deadzone:
            raise DeadZoneException()
        return data


    def calc_stop(self):
        self.send_command(COMMAND.CalcStop)


    def calc_start(self):
        self.send_command(COMMAND.CalcStart)


    def save_settings(self):
        self.send_command(COMMAND.SetEnd)
        if not self.sm.check_parameter_update():
            raise Exception("Parameter is not updated. Did you set new parameters?")


    def reset(self, trial_num = 10):
        self.send_command(COMMAND.Reset)
        if not self.sm.check_parameter_update():
            raise Exception("Reset is failed.")


    def start_map_building(self):
        self.send_command(COMMAND.MapModeStart)
        self.is_building_map = True
        self.find_map_id = 1


    def find_next_map_id(self, ignore_deadzone=False):
        res, new_id, is_last_marker, is_deadzone = self.sm.read_new_mapid(timeout=None, ignore_deadzone=ignore_deadzone)
        if is_deadzone:
            raise DeadZoneException()
        self.find_map_id += 1
        if is_last_marker:
            self.sm.check_parameter_update()
            self.is_building_map = False
        return new_id


    def wait_leave_deadzone(self):
        while re.match(serial_manager.DEAD_ZONE_MESSAGE_REGEX, self.sm.current_line):
            self.sm.fetch_next_line()
        return


    def calc_height(self):
        #TODO:
        print("Not implemented!!")
        self.send_command(COMMAND.HeightCalc)
        if not self.sm.check_parameter_update():
            raise Exception("Parameter is not updated. Did you set new parameters?")


    def send_command(self, command, trial_num=5):
        if not isinstance(command, COMMAND):
            command = COMMAND(command)  # check command in COMMAND Class
        msg = command.value
        for i in range(trial_num):
            self.sm.send_write_message(msg)
            if self.sm.check_ack(msg):
                return
        raise Exception("Failed " + msg + " command")


    def write_parameter(self, parameter, value, trial_num=5):
        if not isinstance(parameter, PARAMETER):
            parameter = PARAMETER(parameter)  # check parameter in PARAMETER Class
        msg = parameter.value
        for i in range(trial_num):
            self.sm.send_write_message(msg, value)
            if self.sm.check_ack(msg, value):
                return
        raise Exception("Failed write parameter: " + msg)


    def read_parameter(self, parameter, trial_num=5):
        if not isinstance(parameter, PARAMETER):
            parameter = PARAMETER(parameter)  # check parameter in PARAMETER Class
        msg = parameter.value
        for i in range(trial_num):
            self.sm.send_read_message(msg)
            if self.sm.check_ack(msg):
                val = self.sm.read_return_value(msg)
                return val
        raise Exception("Failed read parameter: " + msg)
