#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time
import re


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


class SerialManager(object):
    """docstring for SerialManager"""
    def __init__(self, serial_device_name):
        super(SerialManager, self).__init__()
        self.serial = serial.Serial(serial_device_name,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=0)


    def read_line(self, timeout=None):
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
