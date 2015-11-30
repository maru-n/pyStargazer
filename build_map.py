#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pystargazer import *

serial_device = sys.argv[1]
sg = StarGazer(serial_device)

sg.calc_start()
current_status = sg.read_status(timeout=1)
sg.calc_stop()

print("Number of Landmark?")
while True:
    print(">>", end="")
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
    print(">>", end="")
    in_str = input()
    if in_str == "" and current_status:
        ref_id = current_mark_id
        print(ref_id)
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
print(">>", end="")
mark_type = input()
if mark_type == "":
    mark_type = default_mark_type
    print(mark_type)

print("Setting is Ok? (y/n)")
print(">>", end="")
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

def find_new_id_callback(new_id):
    print("Find #" + str(new_id) + " Don't move!")

def save_new_id_callback(new_id, saved_id_num):
    print("Saved #%i  (%i/%i)" % (new_id, saved_id_num, id_num))
    if total_id_num != id_num:
        print("Go to next marker!")

sg.start_map_building()
while sg.is_building_map:
    print("Go to next marker!")
    i = sg.find_next_map_id()
    print("New Id:", i)

print("Finished!")

sg.calc_start()

while True:
    print(sg.read_raw_output())
