#!/usr/bin/env python3

def writeFloat(fi, fl):
    fi.write(fl.to_bytes(4, byteorder='little', signed=True))
