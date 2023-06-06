from .grammarRule import GrammarRule
from .grammarToken import GrammarToken
from . import grammarLog as logger

def parseTokenSection(content: str) -> [GrammarToken]:
    tokens = set([s.strip() for s in content.split("$token")])
    tokens.remove("")
    tokensOut = []
    for t in tokens:
        t = t.split()
        tokensOut.append(GrammarToken(t[0], "Term__" + t[1]))
        if len(t) > 2: tokensOut[-1].alias = t[2]
    return tokensOut

def parsePrioSection(content: str) -> dict:
    return {}

def parseBaseSection(content: str) -> str:
    return "NTerm__" + content.split("$base")[1].strip()

def parseOneRule(name: str, content: str, grammartokens: [GrammarToken]) -> GrammarRule:
    [tokens, func] = content.split("{", 1)
    tokens = [GrammarToken.getTok(t, grammartokens) for t in tokens.strip().split()]
    func = "}".join(func.split("}")[0:-1]).strip()
    for i in range(100):
        func = func.replace(f"${i}", f"l[{i}]")
    func = eval(f"lambda l : {func}")
    size = len(tokens) - ("<empty>" in tokens)
    return GrammarRule(tokens, size, "NTerm__" + name, func)

def parseRuleSection(content: str, tokens: [GrammarToken]) -> [GrammarRule]:
    rules = content.split("$$")
    rulesOut = []
    for r in rules:
        [name, content] = r.split(":=")
        rulesOut += [parseOneRule(name.strip(), c, tokens) for c in content.split("|")]
    return rulesOut

def affectPrios(tokens: [GrammarToken], prios: dict):
    pass

def parseGrammarFile(content: str) -> ([GrammarToken], [str], str, [GrammarRule]):
    sections = content.replace('\n', ' ').split("$$$$")
    [tokenSection, prioSection, baseSection, ruleSection] = sections
    tokens = parseTokenSection(tokenSection) 
    affectPrios(tokens, parsePrioSection(prioSection))
    base = parseBaseSection(baseSection)
    rules = parseRuleSection(ruleSection, tokens)
    return tokens, base, rules

"""
extract output of rules as non terminal symboles
"""
def extractNonTerminalsFromRules(rules: [GrammarRule]) -> [str]:
    nonTerm = set()
    for r in rules: nonTerm.add(r.out)
    return list(nonTerm)

"""
check if all symboles used in rule are among tokens and nonTerm
"""
def checkRule(rule: GrammarRule, tokens: [GrammarToken], nonTerm: [str]):
    for token in rule.tokens:
        if token in nonTerm or token == "<empty>": continue
        if token in [t.tok for t in tokens]: continue
        logger.error("unknown symbole: " + token)
        exit(1)

def memoNonTerm(func):
    mem = {}
    def wrapper(*args, **kwargs):
        if args[0] in mem.keys():
            return mem[args[0]]
        res = func(*args, **kwargs)
        mem[args[0]] = res
        return res
    return wrapper

@memoNonTerm
def firsts(nonTerm: str, rules: [GrammarRule], tokens: [GrammarToken], ignore = set()):
    ignore.update([nonTerm])
    out = set()
    for r in rules:
        if r.out != nonTerm: continue
        firstSymbole = r.tokens[0]
        if firstSymbole in [t.tok for t in tokens]:
            out.update([firstSymbole])
        elif firstSymbole not in ignore:
            out.update(firsts(firstSymbole, rules, tokens, ignore))
    return list(out) 

@memoNonTerm
def follows(nonTerm: str, rules: [GrammarRule], tokens: [GrammarToken], ignore = set()):
    ignore.update([nonTerm])
    out = set()
    for r in rules:
        positions = []
        for i, t in enumerate(r.tokens):
            if t == nonTerm: positions.append(i)
        if len(positions) == 0: continue
        for p in positions:
            if p >= len(r.tokens) - 1:
                if r.out not in ignore:
                    out.update(follows(r.out, rules, tokens, ignore))
            else:
                next = r.tokens[p+1]
                if next in [t.tok for t in tokens]:
                    out.update([next])
                else:
                    out.update(firsts(next, rules, tokens))
    return list(out)

def affectFirstAndFollow(nonTerm: [str], rules: [GrammarRule], tokens: [GrammarToken]):
    res = {}
    for nt in nonTerm:
        res[nt] = {"firsts": firsts(nt, rules, tokens), "follows": follows(nt, rules, tokens)}
    for k,v in res.items():
        print(k,v)

class GrammarFile:
    def __init__(self, filename):
        # read file
        with open(filename, "r") as f:
            self.content = f.read()

        # parse file
        self.tokens, self.base, self.rules = parseGrammarFile(self.content)
 
        # check rules and base for terminal and non terminal symboles
        self.nonTerm = extractNonTerminalsFromRules(self.rules)
        if self.base not in self.nonTerm:
            logger.error(f"base non terminal '{self.base}' has no producing rule")
            exit(1)
        [checkRule(r, self.tokens, self.nonTerm) for r in self.rules]

        # affect first and follow of non terminal
        #affectFirstAndFollow(self.nonTerm, self.rules, self.tokens)

        # affect rule id
        for i, r in enumerate(self.rules):
            r.i = i


def main():
    file = GrammarFile("grammarDef.txt")
    for r in file.rules:
        print(r)

if __name__ == "__main__":
    main()
