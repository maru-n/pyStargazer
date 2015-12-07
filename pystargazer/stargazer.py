#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import serial_manager
from enum import Enum
import re


class DeadZoneException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return repr("DeadZone")


class COMMAND(Enum):
    CalcStop = 'CalcStop'
    CalcStart = 'CalcStart'
    SetEnd = 'SetEnd'
    Reset = 'Reset'
    HeightCalc = 'HeightCalc'
    MapModeStart = 'MapMode|Start'


class PARAMETER(Enum):
    Version = 'Version'
    BaudRate = 'BaudRate'
    IDNum = 'IDNum'
    RefID = 'RefID'
    HeightFix = 'HeightFix'
    MarkHeight = 'MarkHeight'
    MarkType = 'MarkType'
    MarkMode = 'MarkMode'


class StarGazer(object):
    """docstring for StarGazer"""
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
