#!/usr/bin/python3

import os, sys
from fcntl import ioctl

# ioctl commands defined at the pci driver
RD_SWITCHES   = 24929
RD_PBUTTONS   = 24930
WR_L_DISPLAY  = 24931
WR_R_DISPLAY  = 24932
WR_RED_LEDS   = 24933
WR_GREEN_LEDS = 24934

def read_button():
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, RD_PBUTTONS)
    red = os.read(fd, 4); # read 4 bytes and store in red var
    red_number = int.from_bytes(red, 'little')
    os.close(fd)

    if red_number == 7:
        return 'LEFT'
    elif red_number == 11:
        return 'DOWN'
    elif red_number == 13:
        return 'UP'
    elif red_number == 14:
        return "RIGHT"
    elif red_number == 6:
        return "LEFT+RIGHT"

    return ''

def write_right_display(data):
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, WR_R_DISPLAY)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    os.close(fd)

def dec_to_7seg(number):
    if number == 0:
        return 0x40404040
    elif number == 1:
        return 0x40404079
    elif number == 2:
        return 0x4040405b
    elif number == 3:
        return 0b01001111
    elif number == 4:
        return 0b01100110
    elif number == 5:
        return 0b01101101
    elif number == 6:
        return 0b01111101
    elif number == 7:
        return 0b00000111
    elif number == 8:
        return 0b01111111
    elif number == 9:
        return 0b01101111
    else:
        return 0b00000000
    
write_right_display(dec_to_7seg(2))