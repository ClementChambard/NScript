#ifndef VM_H_
#define VM_H_

#include "VMisInGame.h"
#include <iostream>
#include <vector>

#ifdef VM_INGAME
class Player;
#endif

class SdasVM {
public:
    SdasVM();
    #ifdef VM_STANDALONE
    SdasVM(char* script) : SdasVM() { this->script = script; }
    #endif
    #ifdef VM_INGAME
    SdasVM(Player* p) : SdasVM() { this->p = p; }
    #endif

    void setScript(char* script) { if (this->script != nullptr) delete[] this->script; this->script = script; }
    void setScriptFromFile(std::string const& filename);

    void Reset();
    bool Done();
    void Tick();

    static std::vector<int32_t> stack;
private:
    void exec_ins(uint16_t offset);
    int getIntVal(int i);
    float getFloatVal(float f);
    int& getIntRef(int i);
    float& getFloatRef(float f);

    #ifdef VM_INGAME
    Player* p;
    #endif
    bool active = false;
    char* script = nullptr;
    int16_t time = 0;
    uint32_t offset = 0;
    int32_t int_register[10];
    float float_register[10];
    std::vector<std::pair<int16_t,uint32_t>> call_stack;
};

#endif // VM_H_
