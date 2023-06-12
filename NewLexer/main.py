import lexer as lex

lexer = lex.Lexer()

i = lexer.auto_add_symboles([["=", ";", "@", "{", "}", ":"]])
lexer.auto_add_keywords(["type"], priority=i)
i += 1

lexer.add_token(lex.LexerToken(lex.match_ident, i))
lexer.add_token(lex.LexerToken(lex.match_num, i))

lexer.set_text(
    """
type t @ t2 {
  int a @ a1 = 100;
}
"""
)

print(lexer.text)
for t in lexer.lex():
    print(t)
