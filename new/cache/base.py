content = ""

CACHE = None
from cache.cache_type import CacheType
from cache.cache_file import CacheFile

class Cache:
    def __init__(self, filename):
        self.filename = filename
        self.files: [CacheFile] = []
        self.types: [CacheType] = []
        self.buff: str = ""
        # TODO open
        content = ""
        with open(filename, "r") as f:
            content = f.read()
        dat = content.split()
        if len(dat) < 1:
            return
        nbFile = int(dat[0])
        dat = dat[1:]
        for i in range(nbFile):
            n = int(dat[2])
            self.files.append(CacheFile(dat[0], dat[1], [int(dat[j]) for j in range(3, 3+n)]))
            dat = dat[n+3:]
        nbTypes = int(dat[0])
        dat = dat[1:]
        for i in range(nbTypes):
            n = int(dat[2]) * 4
            self.types.append(CacheType(dat[0], dat[1], toParse=dat[3:3+n]))
            dat = dat[n+3:]
        for f in self.files: f.load(self)
        pass

    def file(self, name: str) -> CacheFile:
        return self.files[self.fileId(name)]

    def fileOrNew(self, name: str) -> CacheFile:
        id = self.fileId(name)
        if id >= 0: return self.files[id]
        self.files.append(CacheFile(name, 0, []))
        return self.files[-1]

    def fileId(self, name: str) -> int:
        for i, f in enumerate(self.files):
            if f.name == name:
                return i
        return -1

    def typeId(self, name: str) -> CacheType:
        for i, t in enumerate(self.types):
            if t.name == name:
                return i;
        return -1

    def type_(self, name: str) -> CacheType:
        return self.types[self.typeId(name)]

    def typeOrNew(self, name: str) -> CacheType:
        for t in self.types:
            if t.name == name:
                return t;
        self.types.append(CacheType(name, name, []))
        return self.types[-1]

    def save(self) -> ():
        self.buff = f"{len(self.files)} "
        for f in self.files: self.buff += f.save(self)
        self.buff += str(len(self.types)) + " "
        for t in self.types: self.buff += t.save()
        with open(self.filename, "w") as f:
            f.write(self.buff)



CACHE = Cache(".ns.cache")
