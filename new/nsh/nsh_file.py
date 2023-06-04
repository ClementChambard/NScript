import nsh.parser as parser

import os
import sys
import time
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import fileData as file
import cache.cache_file as cache_file
import cache.cache_type as cache_type
from cache.base import CACHE

def compile(filename: str):
    # should compile file ?
    
    if CACHE.fileId(filename) >= 0 and not CACHE.file(filename).hasChanged(CACHE):
        print (filename + ": Nothing to do")
        return
    dep = []
    file.Open(filename)

    # compile to types
    # should support multiple : TODO
    ts = parser.parseAll()

    # interface ... TODO

    # for each type/interface :
    for t in ts:
        # should regenerate files ?
        shouldRegen = CACHE.typeId(t.name) < 0
        if not shouldRegen: shouldRegen = CACHE.type_(t.name).hasChanged(t, CACHE)
        if  shouldRegen: 
            CACHE.typeOrNew(t.name).update(t)

            # generate
            with open(f"{t.cpp}.hpp", "w") as f:
                f.write(t.to_hpp())
        else:
            print(t.name + ": unchanged")

        CACHE.fileOrNew(t.cpp+".hpp").update(int(time.time()), [])
        dep.append(t.cpp+".hpp")

    CACHE.fileOrNew(filename).update(int(time.time()), dep)
    CACHE.save()
