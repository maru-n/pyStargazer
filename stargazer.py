#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time
import re
from enum import Enum


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
        self.sm = StarGazerSerialManager(serial_device_name)


    def read_raw_output(self):
        return self.sm.read_line()


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


STX = '~'  # start of text data
ETX = '`'  # end of text data

READ_COMMAND_PREFIX = '@'
WRITE_COMMAND_PREFIX = '#'
RETURN_VALUE_PREFIX = '$'
ACK_PREFIX = '!'
SG_MESSAGE_PREFIX = '*'
VALUE_SEPARATER = '|'

_SEND_CHARACTER_INTERVAL = 0.01
_COMMAND_RESPONSE_WAIT_TIME = 5.0
_COMMAND_TRIAL_NUM = 10


class StarGazerSerialManager(object):
    """docstring for StarGazerSerialManager"""
    def __init__(self, serial_device_name):
        super(StarGazerSerialManager, self).__init__()
        self.serial = serial.Serial(serial_device_name,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=1)


    def read_line(self):
        byte_data = b''
        etx_byte = bytes(ETX, 'ascii')
        while True:
            c = self.serial.read(1)
            if c:
                byte_data += c
                if c == etx_byte:
                    break
            else:
                break
        return byte_data.decode()


    def send_write_message(self, message, arg=None):
        if arg != None:
            message += VALUE_SEPARATER + arg
        b = bytes(STX + WRITE_COMMAND_PREFIX + message + ETX, 'ascii')
        self.send_bytes(b)


    def send_read_message(self, message):
        b = bytes(STX + READ_COMMAND_PREFIX + message + ETX, 'ascii')
        self.send_bytes(b)


    def read_return_value(self, message):
        correct_res_prefix = STX + RETURN_VALUE_PREFIX + message + VALUE_SEPARATER
        res = self.__read_only_required_response(correct_res_prefix)
        if res:
            val = res.split(VALUE_SEPARATER)[1].split(ETX)[0]
            return val
        else:
            return False


    def check_parameter_update(self):
        return self.check_ack("ParameterUpdate")


    def check_ack(self, message, arg=None):
        if arg != None:
            message += VALUE_SEPARATER + arg
        correct_res = STX + ACK_PREFIX + message + ETX
        res = self.__read_only_required_response(correct_res)
        if res:
            return True
        else:
            return False


    def __read_only_required_response(self, required_regex):
        start_time = time.time()
        while (time.time() - start_time) < _COMMAND_RESPONSE_WAIT_TIME:
            res = self.read_line()
            if re.match(required_regex, res):
                return res
        else:
            return False


    def send_bytes(self, _bytes):
        for b in _bytes:
            time.sleep(_SEND_CHARACTER_INTERVAL)
            self.serial.write([b])
