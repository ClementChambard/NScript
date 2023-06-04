
class GrammarToken:
    def __init__(self, name: str, tok: str, alias: str = None):
        self.name = name
        self.tok = tok
        self.alias = [alias, name][alias == None]
        self.prio = 0
        self.assoc = "no"

    def __str__(self):
        return f"{self.name}{['@'+self.alias, ''][self.alias == self.name]}:{self.tok}"

    def __repr__(self):
        return f"GrammarToken(\"{self.name}\", \"{self.tok}\", \"{self.alias}\")"

    def __hash__(self):
        return (name+" "+tok+" "+alias).__hash__()

    def corresponds(self, token: str):
        return token == self.name or token == self.alias

    def getTok(token: str, tokens):
        if token == "<empty>": return token
        for t in tokens:
            if t.corresponds(token):
                return t.tok
        return "NTerm__" + token
