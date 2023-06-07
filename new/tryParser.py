"""
You may want to copy the relevant files (parserGenerator/parser.py and parserGenerator/grammar/grammarRule.py)
inside your project instead of using the entirety of parserGenerator
"""

from lexer import lexAll as lex
from parserGenerator.parser import parse, readDotGram

if __name__ == "__main__":
    rules, stateTable = readDotGram("grammar.gram")
    print(parse(rules, stateTable, lex, """
    type t @ test {
       int8 fieldi = (83+(123 + 3));
       string fields @ alias = ("123"+"123");
       float fieldf = 0.;
    }
    """))
