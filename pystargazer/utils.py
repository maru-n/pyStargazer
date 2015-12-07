#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum


class StarGazerException(Exception):
    """docstring for StarGazerException"""
    def __init__(self, value):
        super(StarGazerException, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


class DeadZoneException(StarGazerException):
    def __init__(self):
        super(DeadZoneException, self).__init__("DeadZone")


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
