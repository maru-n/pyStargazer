#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

MAP_MODE_DATA_REGEX = r'~\^I([0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([\+\-][0-9]+\.?[0-9]+)\|([0-9]+\.?[0-9]+)`'
DEAD_ZONE_MESSAGE_REGEX = r'~\*DeadZone`'
MAP_ID_MESSAGE_REGEX = r'~\*MAPID\|([0-9]+)`'
MAP_DATA_SAVE_REGEX = r'~\!MapDataSave`'
PARAMETER_UPDATE_REGEX = r'~\!ParameterUpdate`'

_SEND_CHARACTER_INTERVAL = 0.01
_CHECK_ACK_WAIT_TIME = 1.0
_READ_RESPONSE_WAIT_TIME = 1.0
_PARAMETER_UPDATE_WAIT_TIME = 30.0


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
        try:
            line = byte_data.decode()
            self.__print_debug("recv: "+line)
            return line
        except Exception as e:
            self.__print_debug(e)
            return ""


    def send_write_message(self, message, arg=None):
        if arg != None:
            message += VALUE_SEPARATER + str(arg)
        b = bytes(STX + WRITE_COMMAND_PREFIX + message + ETX, 'ascii')
        self.send_bytes(b)


    def send_read_message(self, message):
        b = bytes(STX + READ_COMMAND_PREFIX + message + ETX, 'ascii')
        self.send_bytes(b)


    def read_data(self, timeout=None, ignore_deadzone=True):
        if ignore_deadzone:
            reg = MAP_MODE_DATA_REGEX
        else:
            reg = r'(' + MAP_MODE_DATA_REGEX + r')|(' + DEAD_ZONE_MESSAGE_REGEX + r')'
        res = self.read_only_required_response(reg, timeout)
        match = re.search(MAP_MODE_DATA_REGEX, res)
        if match:
            mark_id = int(match.group(1))
            angle = float(match.group(2))
            x = float(match.group(3))
            y = float(match.group(4))
            z = float(match.group(5))
            data = [mark_id, angle, x, y, z]
            return res, data
        elif re.match(DEAD_ZONE_MESSAGE_REGEX, res):
            return res, "DeadZone"
        else:
            return res, None


    def read_new_mapid_message(self, timeout=None):
        res = self.read_only_required_response(MAP_ID_MESSAGE_REGEX, timeout)
        new_id = int(re.search(MAP_ID_MESSAGE_REGEX, res).group(1))
        next_res = self.read_line()
        is_last_marker = bool(re.match(MAP_DATA_SAVE_REGEX, next_res))
        return res, new_id, is_last_marker


    def read_return_value(self, message):
        correct_res_prefix = STX + RETURN_VALUE_PREFIX + message + VALUE_SEPARATER
        res = self.read_only_required_response(correct_res_prefix, _READ_RESPONSE_WAIT_TIME)
        if res:
            val = res.split(VALUE_SEPARATER)[1].split(ETX)[0]
            return val
        else:
            return None


    def check_parameter_update(self):
        res = self.read_only_required_response(PARAMETER_UPDATE_REGEX, _PARAMETER_UPDATE_WAIT_TIME)
        if res:
            return True
        else:
            return False


    def check_ack(self, message, arg=None):
        if arg != None:
            message += VALUE_SEPARATER + str(arg)
        correct_res = STX + ACK_PREFIX + message + ETX
        res = self.read_only_required_response(correct_res, _CHECK_ACK_WAIT_TIME)
        if res:
            return True
        else:
            return False


    def read_only_required_response(self, required_regex, timeout):
        if timeout == None:
            while True:
                res = self.read_line(timeout=timeout)
                if re.match(required_regex, res):
                    return res
        else:
            start_time = time.time()
            remain_time = timeout
            while remain_time >= 0:
                remain_time = timeout - (time.time()-start_time)
                res = self.read_line(timeout=remain_time)
                if re.match(required_regex, res):
                    return res
            else:
                return None


    def send_bytes(self, _bytes):
        for b in _bytes:
            time.sleep(_SEND_CHARACTER_INTERVAL)
            self.serial.write([b])
        self.__print_debug("send: "+str(_bytes))


    def __print_debug(self, msg):
        if DEBUG:
            print('\033[94m [DEBUG] \033[0m', msg)
