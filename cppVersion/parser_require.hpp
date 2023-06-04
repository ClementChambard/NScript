#ifndef PARSER_H_
#define PARSER_H_

#include <map>
#include <list>
#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <numeric>

#define ENUM_IDENTIFIERS(o) \
        o(undefined)                     /* undefined */ \
        o(function)                      /* a pointer to given function */ \
        o(parameter)                     /* one of the function params */ \
        o(variable)                      /* a local variable */

#define ENUM_DATATYPES(o) \
        o(integer) \
        o(real) \
        o(string) \
        o(none)

#define ENUM_EXPRESSIONS(o) \
        o(nop) o(string) o(integer) o(real) o(ident)          /* atoms */ \
        o(add) o(neg) o(mul) o(invert) o(eq) o(gt)            /* transformation */ \
        o(cor) o(cand) o(loop)                                /* logic/loop */ \
        o(fcall)                                              /* param0(param1, param2 ...) */ \
        o(copy)                                               /* assign: param1 <<- param0 */ \
        o(list)                                               /* list of exprs (for function body) */ \
        o(ret)                                                /* return (param0) */

#define o(n) n,
enum class id_type { ENUM_IDENTIFIERS(o) };
#undef o

#define o(n) n,
enum class data_type { ENUM_DATATYPES(o) };
#undef o

#define o(n) n,
enum class ex_type {  ENUM_EXPRESSIONS(o)  };
#undef o

typedef std::list<struct Expression> expr_vec;

struct Ident {
    id_type type = id_type::undefined;
    std::size_t index = 0; // function#, parameter# within surrounding function, variable#
    std::string name;
    data_type dtype = data_type::none;

    Ident() {}
    Ident(id_type it, std::size_t id, std::string const& s, data_type dt) : type(it), index(id), name(s), dtype(dt) {}

    std::string to_string() const {
        std::string it;
        std::string dt;
        #define o(n) if (type==id_type::n) it = #n;
        ENUM_IDENTIFIERS(o)
        #undef o
        #define o(n) if (dtype==data_type::n) dt = #n;
        ENUM_DATATYPES(o)
        #undef o
        return "Identifier \e[35m" + name + "\e[0m : " + it + "_#" + std::to_string(index) + " (" + dt + ")";
    }
};

struct Expression {
    ex_type type;
    Ident ident{};
    std::string scst{};
    int32_t icst = 0;
    float fcst = 0.f;
    expr_vec params;
    // for while & if, param0 is cond & rest is code

    template<typename... T>
    Expression(ex_type t, T&&... args) : type(t), params( {std::forward<T>(args)...} ) {}

    Expression()                : type(ex_type::nop)   {}
    Expression(const Ident& i)  : type(ex_type::ident),   ident(i)            {}
    Expression(Ident&& i)       : type(ex_type::ident),   ident(std::move(i)) {}
    Expression(std::string&& s) : type(ex_type::string),  scst(std::move(s))  {}
    Expression(int32_t i)       : type(ex_type::integer), icst(i) {}
    Expression(float f)         : type(ex_type::real),    fcst(f) {}

    bool is_pure() const;
    bool is_number() const { return type == ex_type::integer || type == ex_type::real; }
    double get_num() const { return type == ex_type::real ? fcst : icst; }

    Expression operator%=(Expression&& b) && { return Expression(ex_type::copy, std::move(b), std::move(*this)); }
};

#define o(n) \
    template<typename... T> \
    inline Expression e_##n(T&&... args) { return Expression(ex_type::n, std::forward<T>(args)...); }
ENUM_EXPRESSIONS(o)
#undef o

#define o(n) \
    inline bool is_##n(const Expression& e) { return e.type == ex_type::n; }
ENUM_EXPRESSIONS(o)
#undef o

struct Sub
{
    std::string name;
    Expression code;
    unsigned num_vars = 0, num_params = 0;
    bool pure = false, pure_known = false;

    Expression maketemp() { Expression r(Ident{id_type::variable, num_vars, "$C" + std::to_string(num_vars), data_type::none}); ++num_vars; return r; }
};

struct lexcontext;

#endif // PARSER_H_
