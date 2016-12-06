#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
import warnings


class StargazerException(Exception):
    """docstring for StargazerException"""
    def __init__(self, value):
        super(StargazerException, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


class DeadZoneException(StargazerException):
    def __init__(self):
        super(DeadZoneException, self).__init__("DeadZone")


class COMMAND_MULTI_ID(Enum):
    CalcStop = 'CalcStop'
    CalcStart = 'CalcStart'
    SetEnd = 'SetEnd'
    Reset = 'Reset'
    HeightCalc = 'HeightCalc'


class COMMAND_SINGLE_ID(Enum):
    CalcStop = 'CalcStop'
    CalcStart = 'CalcStart'
    SetEnd = 'SetEnd'
    Reset = 'Reset'
    HeightCalc = 'HeightCalc'
    MapModeStart = 'MapMode|Start'


class PARAMETER_MULTI_ID(Enum):
    Version = 'Version'
    BaudRate = 'BaudRate'
    HeightFix = 'HeightFix'
    MarkHeight = 'MarkHeight'
    MarkType = 'MarkType'


class PARAMETER_SINGLE_ID(Enum):
    Version = 'Version'
    BaudRate = 'BaudRate'
    HeightFix = 'HeightFix'
    MarkHeight = 'MarkHeight'
    MarkType = 'MarkType'
    IDNum = 'IDNum'
    RefID = 'RefID'
    MarkMode = 'MarkMode'

class MESSAGE_UTIL(object):
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
