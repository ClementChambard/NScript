#!/usr/bin/env python3

def writeInt(f, i):
    f.write(i.to_bytes(4, byteorder='little', signed=True))
