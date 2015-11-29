#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .serial_manager import *
from enum import Enum
import re


class COMMAND(Enum):
    CalcStop = 'CalcStop'
    CalcStart = 'CalcStart'
    SetEnd = 'SetEnd'
    Reset = 'Reset'
    HeightCalc = 'HeightCalc'
    MapMode = 'MapMode'


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
        self.sm = SerialManager(serial_device_name)


    def read_raw_output(self, timeout=None):
        output = self.sm.read_line(timeout = timeout)
        return output

    def read_status(self, timeout=None):
        start_time = time.time()
        reg = r'~\^I([0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([0-9]+\.?[0-9]+)`'
        remain_time = timeout
        while (timeout==None) or (remain_time >= 0.):
            raw_output = self.read_raw_output(timeout=remain_time)
            match = re.search(reg, raw_output)
            if match:
                mark_id = int(match.group(1))
                angle = float(match.group(2))
                x = float(match.group(3))
                y = float(match.group(4))
                z = float(match.group(5))
                return mark_id, angle, x, y, z
            elif timeout != None:
                remain_time = timeout - (time.time() - start_time)
        return None

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
