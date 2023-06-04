import time
from cache.cache_util import fileChanged
import os
import stat

class CacheFile:
    def __init__(self, name: str, timestamp: int, dep: [int]):
        self.name = name
        self.timestamp = timestamp
        self.depIds = dep

    def load(self, CACHE):
        self.dep = [CACHE.files[i].name for i in self.depIds]

    def save(self, CACHE):
        self.depIds = [CACHE.fileId(f) for f in self.dep]
        buf = self.name + " " + str(self.timestamp) + " " + str(len(self.dep)) + " "
        for d in self.depIds: buf += str(d) + " "
        return buf

    def hasChanged(self, CACHE):
        if fileChanged(self.name, self.timestamp): return True
        for d in self.dep:
            if fileChanged(d, CACHE.file(d).timestamp): return True
        return False

    def update(self, timestamp: int, dep: [str]):
        self.timestamp = timestamp
        self.dep = dep

