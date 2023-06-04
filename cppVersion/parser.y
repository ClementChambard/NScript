%skeleton "lalr1.cc"
%define api.parser.class {nscr_parser}
%define api.token.constructor
%define api.value.type variant
%define parse.assert
%define parse.error verbose
%locations

%code requires
{
#include "parser_require.hpp"
} // %code requires

%code {

struct lexcontext {
    const char* cursor;
    yy::location loc;
    std::vector<std::map<std::string, Ident>> scopes;
    std::vector<Sub> sub_list;
    unsigned tempCounter = 0;
    Sub sub;
public:
    const Ident& define(const std::string& name, Ident&& f) {
        auto r = scopes.back().emplace(name, std::move(f));
        if (!r.second) throw yy::nscr_parser::syntax_error(loc, "Duplicate definition (" + name + ")");
        return r.first->second;
    }
    Expression defvar(const std::string& name, data_type t = data_type::integer) { return define(name, Ident(id_type::variable , sub.num_vars++  , name, t)); }
    Expression defsub(const std::string& name, data_type t = data_type::integer) { return define(name, Ident(id_type::function , sub_list.size() , name, t)); }
    Expression defpar(const std::string& name, data_type t = data_type::integer) { return define(name, Ident(id_type::parameter, sub.num_params++, name, t)); }
    Expression temp(data_type t = data_type::integer)                            { return defvar("$I" + std::to_string(tempCounter++), t); }
    Expression use(const std::string& name) {
        for (auto j = scopes.crbegin(); j != scopes.crend(); ++j)
            if (auto i = j->find(name); i != j->end())
                    return i->second;
        throw yy::nscr_parser::syntax_error(loc, "Undefined identifier (" + name + ")");
    }
    void add_sub(std::string&& name, Expression&& code) {
        sub.code = e_list(std::move(code));
        sub.name = std::move(name);
        sub_list.push_back(std::move(sub));
        sub = {};
    }
    void operator++() { scopes.emplace_back(); } // enter scope
    void operator--() { scopes.pop_back();     } // exit scope
};

namespace yy { nscr_parser::symbol_type yylex(lexcontext& ctx); }

#define M(x) std::move(x)
#define C(x) Expression(x)
        
} // %code

%param { lexcontext& ctx } //%param

%token END 0
%token RETURN "return" VAR "var" IF "if" WHILE "while" HBEGIN "#begin" HEND "#end" HSUB "#sub"
%token ID ICST FCST SCST CCST
%token OR "||" AND "&&" EQ "==" NE "!=" GE ">=" LE "<="

%left ','
%right '='
%left "||"
%left "&&"
%left "==" "!="
%left '<' '>' "<=" ">="
%left '+' '-'
%left '*' '/'
%right '!'
%left '('

%type   <int32_t>       ICST
%type   <std::string>   SCST ID identifier1
%type   <char>          CCST
%type   <float>         FCST
%type   <Expression>    expr l_expr stmt l_stmt

%%

prog:                             header { ++ctx; } l_sub mainsub l_sub { --ctx; };
header:                           %empty;

l_sub:                            %empty
|                                 "#sub" ID { ctx.defsub($2); ++ctx; } l_param_opt colon1 l_stmt { ctx.add_sub(M($2), M($6)); --ctx; } "#end" l_sub;

l_param_opt:                      %empty | l_param;
l_param:                          param
|                                 param ',' l_param;
param:                            '%' identifier1                           { ctx.defpar($2, data_type::real   ); }
|                                 '$' identifier1                           { ctx.defpar($2, data_type::integer); }
|                                 '^' identifier1                           { ctx.defpar($2, data_type::string ); }

mainsub:                          { ++ctx; } "#begin" colon1 l_stmt "#end"  { --ctx; ctx.add_sub("main_sub", M($4)); };

identifier1:        error{}     | ID                                        { $$ = M($1); };
colon1:             error{}     | ':';
semicolon1:         error{}     | ';';
rparens1:           error{}     | ')';

l_stmt:                           %empty                                    { $$ = e_list(); }
|                                 l_stmt stmt                               { $$ = M($1); $$.params.push_back(M($2)); };

stmt:                             "if" '(' expr rparens1 stmt               { $$ = e_cand(M($3), M($5)); }
|                                 "while" '(' expr rparens1 stmt            { $$ = e_loop(M($3), M($5)); }
|                                 expr semicolon1                           { $$ = M($1);                }
|                                 "var" '%' identifier1 semicolon1          { $$ = ctx.defvar($3, data_type::real) %= 0.f;  }
|                                 "var" '$' identifier1 semicolon1          { $$ = ctx.defvar($3, data_type::integer) %= 0; }
|                                 "var" '^' identifier1 semicolon1          { $$ = ctx.defvar($3, data_type::string) %= std::string(""); }
|                                 "return" expr  semicolon1                 { $$ = e_ret(M($2));         }
|                                 identifier1 '=' expr  semicolon1          { $$ = ctx.use($1) %= M($3); }
|                                 { ++ctx; } '{' l_stmt '}'                 { --ctx; $$ = M($3);         }
|                                 ';'                                       { };

l_expr:                           expr                                      { $$ = e_list(M($1));        }
|                                 l_expr ',' expr                           { $$ = M($1); $$.params.push_back(M($3)); };

expr:                             ID                                        { $$ = ctx.use($1);          }
|                                 ICST                                      { $$ = $1;                   }
|                                 FCST                                      { $$ = $1;                   }
|                                 SCST                                      { $$ = M($1);                }
|                                 CCST                                      { $$ = $1;                   }
|                                 '(' expr  rparens1                        { $$ = M($2);                }
|                                 ID '(' ')'                                { $$ = e_fcall(ctx.use($1)); }
|                                 ID '(' l_expr rparens1                    { $$ = e_fcall(ctx.use($1)); $$.params.splice($$.params.end(), M($3.params)); }
//|                                 '@' ID '(' ')'                          /* differentiate subcall & ins call ? */
//|                                 '@' ID '(' l_expr ')'
| expr '+'  error  {$$=M($1);}  | expr '+'  expr                            { $$ = e_add(M($1), M($3));         }
| expr '-'  error  {$$=M($1);}  | expr '-'  expr                            { $$ = e_add(M($1), e_neg(M($3)));  }
| expr '*'  error  {$$=M($1);}  | expr '*'  expr                            { $$ = e_mul(M($1), M($3));         }
| expr '/'  error  {$$=M($1);}  | expr '/'  expr                            { $$ = e_mul(M($1), e_invert(M($3)));         }
| expr "||" error  {$$=M($1);}  | expr "||" expr                            { $$ = e_cor(M($1), M($3));         }
| expr "&&" error  {$$=M($1);}  | expr "&&" expr                            { $$ = e_cand(M($1), M($3));        }
| expr "==" error  {$$=M($1);}  | expr "==" expr                            { $$ = e_eq(M($1), M($3));          }
| expr "!=" error  {$$=M($1);}  | expr "!=" expr                            { $$ = e_eq(e_eq(M($1), M($3)), 0); }
| expr ">=" error  {$$=M($1);}  | expr ">=" expr                            { $$ = e_eq(e_gt(M($3), M($1)), 0); }
| expr "<=" error  {$$=M($1);}  | expr "<=" expr                            { $$ = e_eq(e_gt(M($1), M($3)), 0); }
| expr '>'  error  {$$=M($1);}  | expr '>'  expr                            { $$ = e_gt(M($1), M($3));          }
| expr '<'  error  {$$=M($1);}  | expr '<'  expr                            { $$ = e_gt(M($3), M($1));          }
|   '-'     error  {}           | '-' expr  %prec '!'                       { $$ = e_neg(M($2));                }
|   '+'     error  {}           | '+' expr  %prec '!'                       { $$ = M($2);                       }
|   '!'     error  {}           | '!' expr                                  { $$ = e_eq(M($2), 0);              };

%%

yy::nscr_parser::symbol_type yy::yylex(lexcontext& ctx)
{
    const char* anchor = ctx.cursor;
    ctx.loc.step();
    auto s = [&](auto func, auto&&... params) { ctx.loc.columns(ctx.cursor - anchor); return func(params..., ctx.loc); };
%{ /* Begin re2c lexer */
re2c:yyfill:enable = 0;
re2c:define:YYCTYPE = "char";
re2c:define:YYCURSOR = "ctx.cursor";
re2c:define:YYMARKER = "ctx.cursor";

// Keywords
"return"               { return s(nscr_parser::make_RETURN); }
"while"                { return s(nscr_parser::make_WHILE);  }
"var"                  { return s(nscr_parser::make_VAR);    }
"if"                   { return s(nscr_parser::make_IF);     }
"#begin"               { return s(nscr_parser::make_HBEGIN); }
"#end"                 { return s(nscr_parser::make_HEND);   }
"#sub"                 { return s(nscr_parser::make_HSUB);   }

"true"                 { return s(nscr_parser::make_ICST, 1); }
"false"                { return s(nscr_parser::make_ICST, 0); }
"null"                 { return s(nscr_parser::make_ICST, 0); }

// Identifiers :
[a-zA-Z_] [a-zA-Z0-9_]* { return s(nscr_parser::make_ID, std::string(anchor, ctx.cursor)); }

// Constant literals :
"\"" [^\"]* "\""       { return s(nscr_parser::make_SCST, std::string(anchor+1, ctx.cursor-1)); }
[0-9]+                 { return s(nscr_parser::make_ICST, std::stoi(std::string(anchor, ctx.cursor))); }
[0-9]+ "." "f"? | ([0-9]+)? "." [0-9]+ "f"? { return s(nscr_parser::make_FCST, std::stof(std::string(anchor, ctx.cursor))); }
"'" . "'"              { return s(nscr_parser::make_ICST, *(anchor+1)); }
/* TODO: other cst literals */

// Whitespace & comments :
"\000"                 { return s(nscr_parser::make_END);    }
"\r\n" | [\n\r]        { ctx.loc.lines();   return yylex(ctx); }
"//" [^\n\r]*          {                    return yylex(ctx); }
[\t\v\b\f ]            { ctx.loc.columns(); return yylex(ctx); }

// Multichar operators & Multichar types
"||"                   { return s(nscr_parser::make_OR);     }
"&&"                   { return s(nscr_parser::make_AND);    }
"=="                   { return s(nscr_parser::make_EQ);     }
"!="                   { return s(nscr_parser::make_NE);     }
">="                   { return s(nscr_parser::make_GE);     }
"<="                   { return s(nscr_parser::make_LE);     }
.                      { return s([](auto...s){return nscr_parser::symbol_type(s...);}, nscr_parser::token_type(ctx.cursor[-1]&0xFF)); }

%} /* End lexer */

}

void yy::nscr_parser::error(const location_type& l, const std::string& m)
{
    std::cerr << (l.begin.filename ? l.begin.filename->c_str() : "(undefined)");
    std::cerr << ':' << l.begin.line << ':' << l.begin.column << '-' << l.end.column << ": " << m << '\n';
}

std::vector<Sub> sub_list;

static bool pure_fcall(const Expression& exp) {
    if (const auto& p = exp.params.front(); is_ident(p) && (p.ident.type == id_type::function))
        if (auto called_function = p.ident.index; called_function < sub_list.size())
            if (const auto& f = sub_list[called_function]; f.pure_known && f.pure) return true;
    return false;
}

static void FindPureFunctions() {
    for (auto& f : sub_list) f.pure_known = f.pure = false;
    do {} while (std::count_if(sub_list.begin(), sub_list.end(), [&](Sub& f){
        if (f.pure_known) return false;
        std::cerr << "Identifying " << f.name << '\n';

        bool unknown_functions = false;
        bool side_effects = false;
        for (auto const& exp : f.code.params) {
            if (is_copy(exp)) side_effects = side_effects || false; // no pointers
            if (is_fcall(exp)) {
                const auto& e = exp.params.front();
                if (!is_ident(e) || e.ident.type != id_type::function) side_effects = side_effects || true;
                const auto& u = sub_list[e.ident.index];
                if (u.pure_known && !u.pure) side_effects = side_effects || true;
                if (!u.pure_known && e.ident.index != (&f - &sub_list[0])) {
                    unknown_functions = true;
                }
            }
        }

        if (side_effects || !unknown_functions) {
            f.pure_known = true;
            f.pure       = !side_effects;
            std::cerr << "Function " << f.name << (f.pure ? " is pure" : " may have side-effects") << "\n";
            return true;
        }
        return false;
    }));
}

bool Expression::is_pure() const {
    for (const auto& e : params) if (!e.is_pure()) return false;
    switch (type) {
        case ex_type::fcall: return pure_fcall(*this);
        case ex_type::copy:  return false;
        case ex_type::ret:   return false;
        case ex_type::loop:  return false;
        default:             return true;
    }
}

#include <fstream>

std::string stringify(const Expression& e, bool stmt = false);
std::string stringify_op(const Expression& e, const char* sep, const char* delim, bool stmt = false, unsigned first = 0, unsigned limit = ~0u)
{
    std::string result(1, delim[0]);
    const char* fsep = "";
    for (const auto& p : e.params) {
        if (first) { --first; continue; }
        if (!limit--) break;
        result += fsep; fsep = sep; result += stringify(p, stmt);
    }
    if (stmt) result += sep;
    result += delim[1];
    return result;
}
std::string stringify(const Expression& e, bool stmt)
{
    switch(e.type) {
        case ex_type::nop       : return "";
        case ex_type::string    : return "\"" + e.scst + "\"";
        case ex_type::integer   : return std::to_string(e.icst);
        case ex_type::real      : return std::to_string(e.fcst);
        case ex_type::ident     : return e.ident.name;

        case ex_type::add       : return stringify_op(e, " + ", "()");
        case ex_type::mul       : return stringify_op(e, " * ", "()");
        case ex_type::eq        : return stringify_op(e, " == ", "()");
        case ex_type::gt        : return stringify_op(e, " > ", "()");
        case ex_type::cand      : return stringify_op(e, " && ", "()");
        case ex_type::cor       : return stringify_op(e, " || ", "()");
        case ex_type::list      : return stmt ? stringify_op(e, "; ", "{}", true) : stringify_op(e, ", ", "()");

        case ex_type::neg       : return "-(" + (e.params.empty() ? "?" : e.params.size()==1 ? stringify(e.params.front()) : stringify_op(e, "??", "()")) + ")";
        case ex_type::invert    : return "1/(" + (e.params.empty() ? "?" : e.params.size()==1 ? stringify(e.params.front()) : stringify_op(e, "??", "()")) + ")";

        case ex_type::copy      : return stringify(e.params.back()) + " = " + stringify(e.params.front());
        case ex_type::fcall     : return "(" + (e.params.empty() ? "?" : stringify(e.params.front())) + ")" + stringify_op(e,", ","()",false,1);
        case ex_type::loop      : return "while " + stringify(e.params.front()) + " " + stringify_op(e, "; ", "{}", true, 1);
        case ex_type::ret       : return "return " + (e.params.empty() ? "?" : e.params.size()==1 ? stringify(e.params.front()) : stringify_op(e, "??", "()"));
    }
    return "?";
}
std::string stringify_nonrec(const Expression& e) {
    switch(e.type) {
        case ex_type::nop       : return "NOP";
        case ex_type::string    : return "Cst litteral : \e[33m\"" + e.scst + "\"\e[0m";
        case ex_type::integer   : return "Cst litteral : \e[33m" + std::to_string(e.icst) + "\e[0m";
        case ex_type::real      : return "Cst litteral : \e[33m" + std::to_string(e.fcst) + "\e[0m";
        case ex_type::ident     : return e.ident.to_string();

        case ex_type::add       : return "Binary expression : \e[31m+\e[30m ";
        case ex_type::mul       : return "Binary expression : \e[31m*\e[30m ";
        case ex_type::eq        : return "Binary expression : \e[31m==\e[30m ";
        case ex_type::gt        : return "Binary expression : \e[31m>\e[30m ";
        case ex_type::cand      : return "Logical expression : \e[31m&&\e[30m ";
        case ex_type::cor       : return "Logical expression : \e[31m||\e[30m ";
        case ex_type::list      : return "List of statements";

        case ex_type::neg       : return "Negate expr";
        case ex_type::invert    : return "Invert expr";

        case ex_type::copy      : return "Affectation statement";
        case ex_type::fcall     : return "Function call";
        case ex_type::loop      : return "Loop statement";
        case ex_type::ret       : return "Return statement";

        default                 : return "???";
    }
}

static std::string stringify(const Sub& s) { return stringify(s.code, true); }
static std::string stringify_tree(const Sub& s) { return "sub " + s.name + ";\n" + stringify(s) + "\n"; }

std::list<Expression> getParams(Expression const& e) { return e.params; }

static bool equal(const Expression& a, const Expression& b) {
    return (a.type == b.type)
        && (!is_ident(a) || (a.ident.type == b.ident.type && a.ident.index == b.ident.index))
        && (!is_string(a) || a.scst == b.scst)
        && (!is_integer(a) || a.icst == b.icst)
        && (!is_real(a) || a.fcst == b.fcst)
        && std::equal(a.params.begin(), a.params.end(), b.params.begin(), b.params.end(), equal);
}

static void ConstantFolding(Expression& e, Sub& s)
{
    for (auto& e : e.params) ConstantFolding(e, s);

    if (is_add(e) || is_mul(e) || is_list(e) || is_cor(e) || is_cand(e)) {
        for (auto j = e.params.end(); j != e.params.begin(); )
            if ((--j)->type == e.type) {
                auto tmp(M(j->params));
                e.params.splice(j = e.params.erase(j), std::move(tmp));
            }
    }

    switch(e.type) {

        case ex_type::list      :
                e.params.remove_if([](Expression& e){ return e.is_pure(); });
                if (auto r = std::find_if(e.params.begin(), e.params.end(), [](const Expression& e) {
                        return is_ret(e) || is_loop(e) && e.params.front().is_number() && e.params.front().get_num() != 0; })
                        ; r != e.params.end() && ++r != e.params.end()) {
                    e.params.erase(r, e.params.end());
                }
                if (e.params.size() == 0) e = e_nop();
                if (e.params.size() == 1) e = C(M(e.params.front()));
                break;
        case ex_type::add       : {
                float tmp_float = std::accumulate(e.params.begin(), e.params.end(), 0.f,
                        [](float n, auto& p) { return p.is_number() ? n + p.get_num() : n; });
                bool hasToBeFloat = (std::count_if(e.params.begin(), e.params.end(), [](Expression& e){ return is_real(e); }));
                e.params.remove_if([](Expression& e){ return e.is_number(); });
                for (auto j = e.params.begin(); j != e.params.end(); ++j)
                    if (is_neg(*j) && is_add(j->params.front())) {
                        auto tmp(M(j->params.front().params));
                        for (auto& p : tmp) p = e_neg(M(p));
                        e.params.splice(j = e.params.erase(j), M(tmp));
                    }
                if (tmp_float != 0.f) {
                    if (hasToBeFloat) e.params.push_back(tmp_float);
                    else e.params.push_back((int32_t)tmp_float);
                }
                if (std::count_if(e.params.begin(), e.params.end(), is_neg) > e.params.size()/2) {
                    for (auto& p : e.params) p = e_neg(M(p));
                    e = e_neg(M(e));
                }
                else if (e.params.size() == 1) e = C(M(e.params.front()));
                else if (e.params.size() == 0 &&  hasToBeFloat) { e = 0.f; break; }
                else if (e.params.size() == 0 && !hasToBeFloat) { e =   0; break; }
                } break;
        case ex_type::mul       : {
                float tmp_float = std::accumulate(e.params.begin(), e.params.end(), 1.f,
                        [](float n, auto& p) { return p.is_number() ? n * p.get_num() : n; });
                bool hasToBeFloat = (std::count_if(e.params.begin(), e.params.end(), [](Expression& e){ return is_real(e); }));
                if (tmp_float == 0.f &&  hasToBeFloat) { e = 0.f; break; }
                if (tmp_float == 0.f && !hasToBeFloat) { e =   0; break; }
                e.params.remove_if([](Expression& e){ return e.is_number(); });
                for (auto j = e.params.begin(); j != e.params.end(); ++j)
                    if (is_invert(*j) && is_mul(j->params.front())) {
                        auto tmp(M(j->params.front().params));
                        for (auto& p : tmp) p = e_invert(M(p));
                        e.params.splice(j = e.params.erase(j), M(tmp));
                    }
                if (tmp_float != 1.f) {
                    if (hasToBeFloat) e.params.push_back(tmp_float);
                    else e.params.push_back((int32_t)tmp_float);
                }
                if (std::count_if(e.params.begin(), e.params.end(), is_invert) > e.params.size()/2) {
                    for (auto& p : e.params) p = e_invert(M(p));
                    e = e_invert(M(e));
                }
                else if (e.params.size() == 1) e = C(M(e.params.front()));
                else if (e.params.size() == 0 &&  hasToBeFloat) { e = 1.f; break; }
                else if (e.params.size() == 0 && !hasToBeFloat) { e =   1; break; }
                } break;
        case ex_type::neg       :
                if   (is_integer(e.params.front())) e = -e.params.front().icst;
                else if (is_real(e.params.front())) e = -e.params.front().fcst;
                else if (is_neg (e.params.front())) e = C(M(e.params.front().params.front()));
                break;
        case ex_type::invert    :
                if   (is_integer(e.params.front().is_number())) { if (e.params.front().get_num() == 0) { /* Error ? */ } else e = (float)(1/e.params.front().get_num()); }
                else if (is_invert(e.params.front())) e = C(M(e.params.front().params.front()));
                break;
        case ex_type::eq        :
                if (e.params.front().is_number() && e.params.back().is_number()) e = int32_t(e.params.front().get_num() == e.params.back().get_num());
                else if (equal(e.params.front(), e.params.back()) && e.params.front().is_pure()) e = 1;
                break;
        case ex_type::gt        :
                if (e.params.front().is_number() && e.params.back().is_number()) e = int32_t(e.params.front().get_num() > e.params.back().get_num());
                break;
        case ex_type::copy      :
                if (equal(e.params.front(), e.params.back()) && e.params.front().is_pure()) e = e_nop();
                break;
        case ex_type::loop      :
                if (e.params.front().is_number() && !e.params.front().get_num()) e = e_nop();
                break;
        case ex_type::cand      :
        case ex_type::cor       : {
                auto value_kind = is_cand(e) ? [](double v){ return v != 0; } : [](double v){ return v == 0; };
                e.params.erase(std::remove_if(e.params.begin(), e.params.end(), [&](Expression& p){
                        return p.is_number() && value_kind(p.get_num()); }), e.params.end());
                if (auto i = std::find_if(e.params.begin(), e.params.end(), [&](const Expression& p) {
                        return p.is_number() && !value_kind(p.get_num());}); i != e.params.end()) {
                    //while(i != e.params.begin() && std::prev(i)->is_pure()) { --i; }
                    //e.params.erase(i, e.params.end());
                    e = /*e_list(M(e),*/ (is_cand(e) ? 0 : 1);
                }
                else if (e.params.size() == 1) e = C(M(e.params.front()));
                } break;
        //case ex_type::fcall     : return "Function call";
        //case ex_type::ret       : return "Return statement";
        default                 :
                break;

    }
}

static void DoConstantFolding() {
    FindPureFunctions();
    for (Sub& s : sub_list) {
        ConstantFolding(s.code, s);
    }
}

#include "treeView.hpp"

int main(int argc, char** argv)
{
    std::string filename = argv[1];
    std::ifstream f(filename);
    std::string buffer(std::istreambuf_iterator<char>(f), {});

    lexcontext ctx;
    ctx.cursor = buffer.c_str();
    ctx.loc.end.filename = ctx.loc.begin.filename = &filename;

    yy::nscr_parser parser(ctx);
    parser.parse();
    sub_list = std::move(ctx.sub_list);

    std::cerr << "INITIAL : \n";
    for (const auto& s : sub_list) std::cerr << "Sub " << s.name << " :\n" << TreeView(stringify_nonrec, getParams, s.code) << "\n\n";

    DoConstantFolding();

    std::cerr << "\n\n\nFINAL : \n";
    for (const auto& s : sub_list) std::cerr << "Sub " << s.name << " :\n" << TreeView(stringify_nonrec, getParams, s.code) << "\n\n";
}
