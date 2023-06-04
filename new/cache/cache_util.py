import os
import sys
import stat
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

def fileChanged(filename: str, tim: str):
    try:
        if filename[0] != "/": filename = "./" + filename
        stats = os.stat(filename)
        modifyTime = stats[ stat.ST_MTIME ]
        return int(tim)+2 < modifyTime
    except:
        return True
