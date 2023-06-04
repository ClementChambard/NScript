name = "NOFILE"
errors = 0
content = ""
lines = []

def Open(filename: str):
    ls = []
    with open(filename, "r") as f:
        ls = f.readlines()
    startList(ls, filename)

def startList(l: [str], filename = "NOFILE"):
    global errors, lines, name, content
    errors = 0
    lines = l
    name = filename
    content = "".join(l)

def startStr(s: str, filename = "NOFILE"):
    global errors, lines, name, content
    errors = 0
    lines = s.split("\n")
    name = filename
    content = s

