from . import grammarLexer
from .grammar import readGrammar as rg
from .grammar.grammarRule import GrammarRule
from .grammar.grammarToken import GrammarToken
from .grammar.grammarFirstFollow import firsts, follows

from .parser import parse, readDotGram

"""
extract output of rules as non terminal symboles
"""


def extractNonTerminalsFromRules(rules: list[GrammarRule]) -> list[str]:
    nonTerm = set()
    for r in rules:
        nonTerm.add(r.out)
    return list(nonTerm)


"""
check if all symboles used in rule are among tokens and nonTerm
"""


def checkRule(rule: GrammarRule, tokens: list[GrammarToken], nonTerm: list[str]):
    for token in rule.tokens:
        if token in nonTerm or token == "<empty>":
            continue
        if token in [t.tok for t in tokens]:
            continue
        print("unknown symbole: " + token)
        exit(1)


def affectFirstAndFollow(
    nonTerm: list[str], rules: list[GrammarRule], tokens: list[GrammarToken]
):
    res = {}
    for nt in nonTerm:
        res[nt] = {
            "firsts": firsts(nt, rules, tokens),
            "follows": follows(nt, rules, tokens),
        }
    for k, v in res.items():
        print(k, v)


def parseGrammarFile(dat):
    tokenSec, prioSec, baseSec, ruleSec = dat
    base = "NTerm__" + baseSec

    _ = prioSec

    tokens = []
    for t in tokenSec:
        tokens.append(GrammarToken(t["id"], "Term__" + t["name"]))
        if t["alias"] is not None:
            tokens[-1].alias = t["alias"]

    rules = []
    for r in ruleSec:
        name = "NTerm__" + r["produces"]
        intokens = [GrammarToken.getFrom(t, tokens) for t in r["tokens"]]

        func = r["ast"]
        for i in range(100):
            func = func.replace(f"${i}", f"l[{i}]")
        func = f"lambda l : {func}"

        size = len(intokens) - ("<empty>" in intokens)
        rules.append(GrammarRule(intokens, size, name, func))

    return tokens, base, rules


def save_grammar_to_file(grammarFileName: str, outputFileName: str, rules, stateTable):
    txt = ""
    with open(grammarFileName, "r") as f:
        txt = f.read()
    out = parse(rules, stateTable, grammarLexer.lexAll, txt)

    tokens, base, rules = parseGrammarFile(out)

    # check rules and base for terminal and non terminal symboles
    nonTerm = extractNonTerminalsFromRules(rules)
    if base not in nonTerm:
        print(f"base non terminal '{base}' has no producing rule")
        exit(1)
    [checkRule(r, tokens, nonTerm) for r in rules]

    # affect first and follow of non terminal
    # affectFirstAndFollow(self.nonTerm, self.rules, self.tokens)

    # affect rule id
    for i, r in enumerate(rules):
        r.i = i

    stateTable = rg.constructGrammar(tokens, base, rules)

    with open(outputFileName, "w") as f:
        f.write("[" + str(rules))
        f.write(",\n")
        f.write(str(stateTable) + "]")


from inspect import getsourcefile
from os.path import abspath


def grammarGramFile():
    thisfile = abspath(getsourcefile(lambda: 0))
    thisdir = "/".join(thisfile.split("/")[0:-1])
    return f"{thisdir}/parserGeneratorGrammar.gram"


def grammarGramtFile():
    thisfile = abspath(getsourcefile(lambda: 0))
    thisdir = "/".join(thisfile.split("/")[0:-1])
    return f"{thisdir}/parserGeneratorGrammar.gramt"


if __name__ == "__main__":
    grammarText = ""
    rules, stateTable = readDotGram("parserGeneratorGrammar.gram")

    save_grammar_to_file(grammarGramtFile(), "grammar.gram", rules, stateTable)

    txt = ""
    with open("grammar.gram", "r") as f:
        txt = f.read()

    stateTable = []
    rules = []

    rules, stateTable = eval(txt)

    print(str(stateTable))
