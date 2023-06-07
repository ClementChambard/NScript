from typing import Optional


class GrammarToken:
    def __init__(self, name: str, tok: str, alias: Optional[str] = None):
        self.name = name
        self.tok = tok
        self.alias = [alias, name][alias is None]
        self.prio = 0
        self.assoc = "no"

    def __str__(self):
        return f"{self.name}{['@'+self.alias, ''][self.alias == self.name]}:{self.tok}"

    def __repr__(self):
        return f'GrammarToken("{self.name}", "{self.tok}", "{self.alias}")'

    def __hash__(self):
        return (self.name + " " + self.tok + " " + self.alias).__hash__()

    def corresponds(self, token: str):
        return token == self.name or token == self.alias

    @staticmethod
    def getTok(token: str, tokens):
        if token == "<empty>":
            return token
        for t in tokens:
            if t.corresponds(token):
                return t.tok
        return "NTerm__" + token

    @staticmethod
    def getFrom(token: dict, tokens):
        if token is None:
            return "<empty>"
        val = token.get("id", None)
        if val is None:
            val = token["alias"]
        return GrammarToken.getTok(val, tokens)
