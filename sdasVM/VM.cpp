#include "VM.h"

#ifdef VM_INGAME
#include "Player.h"
#endif

#include <fstream>
#include <iostream>

std::vector<int32_t> SdasVM::stack;

SdasVM::SdasVM()
{
    time = 0;
    offset = 0;
    for (int i = 0; i < 10; i++)
    {
        int_register[i] = 0;
        float_register[i] = 0.f;
    }
}

bool SdasVM::Done()
{
    return this->active == false;
}

void SdasVM::Reset()
{
    if (script != nullptr) active = true;
    call_stack.clear();
    offset = 0;
    time = 0;
}

void SdasVM::setScriptFromFile(const std::string &filename)
{
    if (script != nullptr) { delete[] script; script = nullptr; }
    std::ifstream file;
    file.open(filename, std::ios::binary);
    file.seekg(0, std::ios::end);
    auto size = file.tellg();
    file.seekg(0, std::ios::beg);
    size -= file.tellg();
    char* buff = new char[size];
    file.read(buff, size);
    file.close();
    setScript(buff);
}

void SdasVM::Tick()
{
    if (!active || script == nullptr) return;


    uint32_t oldinstr = offset;
    uint16_t instype, inslength;
    int16_t instime;
    #define getIns if (script[offset] == -1) return; \
        instype = *reinterpret_cast<uint16_t*>(&(script[offset])); \
        inslength = *reinterpret_cast<uint16_t*>(&(script[offset+2])); \
        instime = *reinterpret_cast<int16_t*>(&(script[offset+4]));
    getIns;
    while(instime <= time && active)
    {
        //std::cout << offset << '\n';
        exec_ins(offset);
        if (!active) return;

        while (oldinstr != offset)
        {
            getIns;
            oldinstr = offset;
            if(instime <= time)
            {
                exec_ins(offset);
                if (!active) return;
            }
        }
        offset+=inslength;
        oldinstr = offset;
        getIns;
    }
    time++;
}

int SdasVM::getIntVal(int i)
{
    if (i >= 100000 && i < 100010) return int_register[i-100000];
    else if (i == 100050) return stack.back();
    return i;
}

float SdasVM::getFloatVal(float f)
{
    if (f >= 100010 && f < 100020) return float_register[(int)f-100010];
    else if (f == 100051) return *reinterpret_cast<float*>(&stack.back());
    return f;
}

int& SdasVM::getIntRef(int i)
{
    if (i >= 100000 && i < 1000010) return int_register[i-100000];
    else if (i == 100050) return stack.back();
    return int_register[9];
}

float& SdasVM::getFloatRef(float f)
{
    if (f >= 100010 && f < 100020) return float_register[(int)f-100010];
    else if (f == 100051) return *reinterpret_cast<float*>(&stack.back());
    return float_register[9];
}

void SdasVM::exec_ins(uint16_t offset)
{
    char* insLoc = &script[offset];
    uint16_t type = *reinterpret_cast<uint16_t*>(insLoc);
    int32_t ti1, ti2;
    float tf1, tf2;
    #define S(x) getIntVal(*reinterpret_cast<int32_t*>(&insLoc[8+4*x]))
    #define f(x) getFloatVal(*reinterpret_cast<float*>(&insLoc[8+4*x]))
    #define rS(x) getIntRef(*reinterpret_cast<int32_t*>(&insLoc[8+4*x]))
    #define rf(x) getFloatRef(*reinterpret_cast<float*>(&insLoc[8+4*x]))
    #define Str(s) &script[s]
    #define PopS(v) v = stack.back(); stack.pop_back()
    #define Popf(v) v = *reinterpret_cast<float*>(&stack.back()); stack.pop_back()
    #define PushS(v) stack.push_back(v)
    #define Pushf(v) stack.push_back(*reinterpret_cast<int32_t*>(&v))
    #define jmp(x, t) this->offset = x; time = t
    switch (type)
    {
        case 0:
            return;
        case 1:
            if (call_stack.empty()) active = false;
            else
            {
                jmp(call_stack.back().second, call_stack.back().first);
                call_stack.pop_back();
            }
            return;
        case 2:
            call_stack.push_back({time, offset+12});
            jmp(S(0), 0);
            return;
        case 50:
            std::cout << Str(S(0));
            return;
        case 51:
            std::cout << static_cast<char>(S(0));
            return;
        case 52:
            std::cout << S(0);
            return;
        case 53:
            std::cout << f(0);
            return;
        case 99: // dump state (debug)
            std::cout << "\nFULL DUMP\n\nInteger registers :\n";
            for (int i = 0; i < 10; i++)
                std::cout << " - I" << i << " = " << int_register[i] << "\n";
            std::cout << "\nFloat registers :\n";
            for (int i = 0; i < 10; i++)
                std::cout << " - f" << i << " = " << float_register[i] << "\n";
            std::cout << "\nStack :\n";
            for (auto v : stack)
                std::cout << "  " << v << "\n";
            std::cout << "TOP\n\n";
            return;
        case 100: // iset
            rS(0) = S(1);
            return;
        case 101: // fset
            rf(0) = f(1);
            return;
        case 102: // ipsh
            stack.push_back(S(0));
            return;
        case 103: // fpsh
            stack.push_back(S(0));
            return;
        case 104: // ipop
            if (stack.empty()) stack.push_back(0);
            rS(0) = stack.back(); stack.pop_back();
            return;
        case 105: // fpop
            if (stack.empty()) stack.push_back(0);
            rf(0) = *reinterpret_cast<float*>(&stack.back()); stack.pop_back();
            return;
        case 106: // iadd
            rS(0) += S(1);
            return;
        case 107: // fadd
            rf(0) += f(1);
            return;
        case 108: // isub
            rS(0) -= S(1);
            return;
        case 109: // fsub
            rf(0) -= f(1);
            return;
        case 110: // imul
            rS(0) *= S(1);
            return;
        case 111: // fmul
            rf(0) *= f(1);
            return;
        case 112: // idiv
            rS(0) /= S(1);
            return;
        case 113: // fdiv
            rf(0) /= f(1);
            return;
        case 114: // imod
            rS(0) %= S(1);
            return;
        case 115: // fmod
            rf(0) = (int)f(0) % (int)f(1);
            return;
        case 116: // isadd
            rS(0) = S(1) + S(2);
            return;
        case 117: // fsadd
            rf(0) = f(1) + f(2);
            return;
        case 118: // issub
            rS(0) = S(1) - S(2);
            return;
        case 119: // fssub
            rf(0) = f(1) - f(2);
            return;
        case 120: // ismul
            rS(0) = S(1) * S(2);
            return;
        case 121: // fsmul
            rf(0) = f(1) * f(2);
            return;
        case 122: // isdiv
            rS(0) = S(1) / S(2);
            return;
        case 123: // fsdiv
            rf(0) = f(1) / f(2);
            return;
        case 124: // ismod
            rS(0) = S(1) % S(2);
            return;
        case 125: // fsmod
            rf(0) = (int)f(1) % (int)f(2);
            return;
        case 126: // ieq
            rS(0) = S(1) == S(2);
            return;
        case 127: // feq
            rS(0) = f(1) == f(2);
            return;
        case 128: // ineq
            rS(0) = S(1) != S(2);
            return;
        case 129: // fneq
            rS(0) = f(1) != f(2);
            return;
        case 130: // igt
            rS(0) = S(1) >  S(2);
            return;
        case 131: // fgt
            rS(0) = f(1) >  f(2);
            return;
        case 132: // ige
            rS(0) = S(1) >= S(2);
            return;
        case 133: // fge
            rS(0) = f(1) >= f(2);
            return;
        case 134: // ilt
            rS(0) = S(1) <  S(2);
            return;
        case 135: // flt
            rS(0) = f(1) <  f(2);
            return;
        case 136: // ile
            rS(0) = S(1) <= S(2);
            return;
        case 137: // fle
            rS(0) = f(1) <= f(2);
            return;
        case 138: // not
            rS(0) = !S(1);
            return;
        case 139: // and
            rS(0) = S(1) && S(2);
            return;
        case 140: // or
            rS(0) = S(1) || S(2);
            return;
        case 141: // xor
            rS(0) = S(1) ^ S(2);
            return;
        case 142: // istadd
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 + ti2);
            return;
        case 143: // fstadd
            Popf(tf1);
            Popf(tf2);
            tf1 += tf2;
            Pushf(tf1);
            return;
        case 144: // istsub
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 - ti2);
            return;
        case 145: // fstsub
            Popf(tf1);
            Popf(tf2);
            tf1 -= tf2;
            Pushf(tf1);
            return;
        case 146: // istmul
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 * ti2);
            return;
        case 147: // fstmul
            Popf(tf1);
            Popf(tf2);
            tf1 *= tf2;
            PushS(tf1);
            return;
        case 148: // istdiv
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 / ti2);
            return;
        case 149: // fstdiv
            Popf(tf1);
            Popf(tf2);
            tf1 /= tf2;
            PushS(tf1);
            return;
        case 150: // istmod
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 % ti2);
            return;
        case 151: // fstmod
            Popf(tf1);
            Popf(tf2);
            tf1 = (int)tf1 % (int)tf2;
            Pushf(tf1);
            return;
        case 152: // isteq
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 == ti2);
            return;
        case 153: // fsteq
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 == tf2);
            return;
        case 154: // istneq
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 != ti2);
            return;
        case 155: // fstneq
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 != tf2);
            return;
        case 156: // istgt
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 > ti2);
            return;
        case 157: // fstgt
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 > tf2);
            return;
        case 158: // istge
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 >= ti2);
            return;
        case 159: // fstge
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 >= tf2);
            return;
        case 160: // istlt
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 < ti2);
            return;
        case 161: // fstlt
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 < tf2);
            return;
        case 162: // istle
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 <= ti2);
            return;
        case 163: // fstle
            Popf(tf1);
            Popf(tf2);
            PushS(tf1 <= tf2);
            return;
        case 164: // stnot
            stack.back() = !stack.back();
            return;
        case 165: // stand
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 && ti2);
            return;
        case 166: // stor
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 || ti2);
            return;
        case 167: // stxor
            PopS(ti1);
            PopS(ti2);
            PushS(ti1 ^ ti2);
            return;
        case 200: // jmp
            jmp(S(0), S(1));
            return;
        case 201: // jmpdec
            if (rS(2)-- > 0) jmp(S(0), S(1));
            return;
        case 202: // jmpieq
            if (S(2) == S(3)) jmp(S(0), S(1));
            return;
        case 203: // jmpfeq
            if (f(2) == f(3)) jmp(S(0), S(1));
            return;
        case 204: // jmpine
            if (S(2) != S(3)) jmp(S(0), S(1));
            return;
        case 205: // jmpfne
            if (f(2) != f(3)) jmp(S(0), S(1));
            return;
        case 206: // jmpigt
            if (S(2) >  S(3)) jmp(S(0), S(1));
            return;
        case 207: // jmpfgt
            if (f(2) >  f(3)) jmp(S(0), S(1));
            return;
        case 208: // jmpige
            if (S(2) >= S(3)) jmp(S(0), S(1));
            return;
        case 209: // jmpfge
            if (f(2) >= f(3)) jmp(S(0), S(1));
            return;
        case 210: // jmpilt
            if (S(2) <  S(3)) jmp(S(0), S(1));
            return;
        case 211: // jmpflt
            if (f(2) <  f(3)) jmp(S(0), S(1));
            return;
        case 212: // jmpile
            if (S(2) <= S(3)) jmp(S(0), S(1));
            return;
        case 213: // jmpfle
            if (f(2) <= f(3)) jmp(S(0), S(1));
            return;
        case 214: // jmpst
            if (stack.back() != 0) jmp(S(0), S(1));
            stack.pop_back();
            return;
        case 215: // jmpnst
            if (stack.back() == 0) jmp(S(0), S(1));
            stack.pop_back();
            return;
        case 300: // attack
            #ifdef VM_STANDALONE
            std::cout << "\nins_300 (attack) can't be used in standalone mode\n";
            #elifdef VM_INGAME
            p->hitboxes.Attack_noob(S(0), "body", glm::vec3(f(2), f(3), f(4)), glm::vec3(f(5), f(6), f(7)), f(8));
            #endif
            return;
        case 301: // resetHitboxGroup
            #ifdef VM_STANDALONE
            std::cout << "\nins_301 (resetHitboxGroup) can't be used in standalone mode\n";
            #elifdef VM_INGAME
            if (S(0) < -1 && S(0) >= 5) std::cout << "SDASVM: error hitbox group must be between 0 and 4 (got " << S(0) << ")\n";
            else if (S(0) == -1) p->hitboxes.ResetAll();
            else p->hitboxes.ResetGroup(S(0));
            #endif
            return;
        case 302: // resetHitboxes
            #ifdef VM_STANDALONE
            std::cout << "\nins_302 (resetHitboxes) can't be used in standalone mode\n";
            #elifdef VM_INGAME
            if (S(0) < -1 && S(0) >= 5) std::cout << "SDASVM: error hitbox group must be between 0 and 4 (got " << S(0) << ")\n";
            else if (S(0) == -1) p->hitboxes.ResetAllBoxes();
            else p->hitboxes.ResetBoxes(S(0));
            #endif
            return;

    }
    #undef Pushf
    #undef PushS
    #undef Popf
    #undef PopS
    #undef jmp
    #undef S
    #undef Str
    #undef rS
    #undef f
    #undef rf
}
