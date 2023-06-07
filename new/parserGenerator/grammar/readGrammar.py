from typing import Tuple
from .grammarRule import GrammarRule
from .grammarStateRule import GrammarStateRule

ruleList: list = []
base = ""
verbose = False


def transitions(stat) -> Tuple[dict, list]:
    shift: dict = {}
    reduce = []
    for r in stat:
        s, rto = r.advance()
        if s == -1 or "<empty>" in r.rule.tokens:
            reduce.append(r.rule.i)
            continue
        to = shift.get(s, set())
        to.add(rto)
        shift[s] = to
    return shift, reduce


def resolveConflicts(shift, reduce, tokens):
    _ = tokens
    # Place the OK and set default
    additionnal = {}
    if shift.get("Term__EOF", "no") != "no":
        shift.pop("Term__EOF")
        additionnal["Term__EOF"] = ["OK"]
    default = ["Err"]
    if len(reduce) > 0:
        # if multiple reduce, should pick the more appropriate
        if len(reduce) > 1:
            if verbose:
                print("reduce/reduce conflicts:")
                for i, p1 in enumerate(reduce):
                    for p2 in reduce[i + 1 :]:
                        print("-", p1, "/", p2)
            # TODO resolve
            # How ???

        # if reduce is not empty, should remove unnecessary shift
        # (shift/reduce conflicts)
        if len(shift) > 0:
            # conflict is when shift is in the follow of the last rule symbole
            # TODO: need follows ?
            if verbose:
                print("possible shift/reduce conflict(s)")

        default = ["R", reduce[0]]
    return shift, default, additionnal


def constructGrammar(tokens, default, rules):
    # get initial state
    axiom = GrammarStateRule(
        GrammarRule([default, "Term__EOF"], 2, "AXIOM", "lambda l : l[0]"), 0
    )
    state0 = GrammarStateRule.completeState([axiom], rules)

    # list of state
    states = [state0]
    # state table
    stateTable = []
    # pile of state to do
    todo = [state0]

    # add state if it doesnt exist, return state id
    def getState(state):
        for i, s in enumerate(states):
            if s == state:
                return i
        states.append(state)
        todo.append(state)
        return len(states) - 1

    # continue while state to do
    while len(todo) > 0:
        current = todo[0]
        todo = todo[1:]
        # get possible transitions
        shift, reduce = transitions(current)
        # resolve conflicts
        shift, default, additionnal = resolveConflicts(shift, reduce, tokens)
        # all shift as states
        for k, s in shift.items():
            shift[k] = GrammarStateRule.completeState(s, rules)
        # for all shift check if state exists
        for k, s in shift.items():
            # getState will create a new one if it doesnt exist
            shift[k] = ["S", getState(s)]
        shift["DEFAULT"] = default
        shift.update(additionnal)
        stateTable.append(shift)

    return stateTable
