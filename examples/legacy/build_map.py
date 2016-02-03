#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)

print("reset stargazer...")
sg.calc_stop()
sg.reset()
sg.write_parameter(PARAMETER.MarkType, 'HLD1L')
sg.write_parameter(PARAMETER.MarkMode, 'Alone')
sg.save_settings()
sg.calc_start()
current_status = sg.read_status(timeout=1)
sg.calc_stop()

print("Number of Landmark?")
while True:
    print(">> ", end="")
    in_str = input()
    try:
        id_num = int(in_str)
        break
    except Exception as e:
        print("Number is required!!")


if current_status:
    current_mark_id = current_status[0]
    print("1st Landmark ID? (current marker is #%i. Default is this.) :" % current_mark_id)
else:
    print("1st Landmark ID? (current marker is not available.)")
while True:
    print(">> ", end="")
    in_str = input()
    if in_str == "" and current_status:
        ref_id = current_mark_id
        print("\033[1A>>", str(ref_id))
        break
    try:
        ref_id = int(in_str)
        break
    except Exception as e:
        pass


default_mark_type = "HLD1L"
print("Mark Type?")
print("HLD1: 1.1<=height<=2.9")
print("HLD2: 2.9<=height<=4.5")
print("HLD3: 4.5<=height<=6.0")
print("HLDxS: 3x3 Landmark,  HLDxL 4x4 Landmark. (Default is %s)" % default_mark_type)
print(">> ", end="")
mark_type = input()
if mark_type == "":
    mark_type = default_mark_type
    print("\033[1A>>", mark_type)

print("Setting is Ok? (y/n)")
print(">> ", end="")
if not input() in ['y', 'Y', 'yes', 'Yes', 'YES']:
    sys.exit()

print("setting up...")

sg.write_parameter(PARAMETER.IDNum, id_num)
sg.write_parameter(PARAMETER.RefID, ref_id)
sg.write_parameter(PARAMETER.HeightFix, 'No')
sg.write_parameter(PARAMETER.MarkType, mark_type)
sg.save_settings()

sg.write_parameter(PARAMETER.MarkMode, 'Map')
sg.save_settings()

print("=== Set up result ===")
for p in PARAMETER:
    res = sg.read_parameter(p)
    print("%10s : %s"%(p.name, res))

sg.start_map_building()
while sg.is_building_map:
    try:
        print("Go to middle point between marker and wait a few secconds.")
        i = sg.find_next_map_id()
        print("New Id:", i, "(%i/%i)"%(sg.find_map_id, id_num))
    except DeadZoneException as e:
        print("Dead zone! go back previous marker...")
        sg.wait_leave_deadzone()
        print("OK! leaved deadzone!")

print("Finished!")

sg.calc_start()

print("# angle, x, y, x")
while True:
    try:
        data = sg.read_status(ignore_deadzone=False)
        print(data[1], data[2], data[3], data[4])
    except DeadZoneException as e:
        print("DeadZone.")
