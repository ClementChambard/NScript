stateTable = [
    {"NTerm__Type":    ["S", 1 ], "Term__KEYWORD_type": ["S", 2 ],                                                    "DEFAULT": ["Err"  ]},
    {"Term__EOF":      ["OK"   ],                                                                                     "DEFAULT": ["Err"  ]},
    {"Term__IDENT":    ["S", 3 ],                                                                                     "DEFAULT": ["Err"  ]},
    {"Term__SYMBOL_@": ["S", 4 ], "NTerm__AliasOpt":    ["S", 6 ],                                                    "DEFAULT": ["R", 2 ]},
    {"Term__IDENT":    ["S", 5 ],                                                                                     "DEFAULT": ["Err"  ]},
    {                                                                                                                 "DEFAULT": ["R", 1 ]},                      
    {"Term__SYMBOL_{": ["S", 7 ],                                                                                     "DEFAULT": ["Err"  ]},
    {"Term__IDENT":    ["S", 12], "NTerm__FieldList":   ["S", 8 ], "NTerm__Field": ["S", 10],                         "DEFAULT": ["R", 4 ]},
    {"Term__SYMBOL_}": ["S", 9 ],                                                                                     "DEFAULT": ["Err"  ]},
    {                                                                                                                 "DEFAULT": ["R", 0 ]},                      
    {"Term__IDENT":    ["S", 12], "NTerm__FieldList":   ["S", 11], "NTerm__Field": ["S", 10],                         "DEFAULT": ["R", 4 ]},
    {                                                                                                                 "DEFAULT": ["R", 3 ]},                      
    {"Term__IDENT":    ["S", 13],                                                                                     "DEFAULT": ["Err"  ]},
    {"Term__SYMBOL_@": ["S", 4 ], "NTerm__AliasOpt":    ["S", 14],                                                    "DEFAULT": ["R", 2 ]},
    {"Term__SYMBOL_=": ["S", 17], "NTerm__DefaultOpt":  ["S", 15],                                                    "DEFAULT": ["R", 7 ]},
    {"Term__SYMBOL_;": ["S", 16],                                                                                     "DEFAULT": ["Err"  ]},
    {                                                                                                                 "DEFAULT": ["R", 5 ]},                      
    {"NTerm__E":       ["S", 18], "Term__INT":          ["S", 19], "Term__FLOAT":  ["S", 20], "Term__STR": ["S", 21], "DEFAULT": ["Err"  ]},
    {                                                                                                                 "DEFAULT": ["R", 6 ]},
    {                                                                                                                 "DEFAULT": ["R", 8 ]},
    {                                                                                                                 "DEFAULT": ["R", 9 ]},
    {                                                                                                                 "DEFAULT": ["R", 10]},
]
