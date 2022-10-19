#include <iostream>
#include <chrono>
#include <thread>
#include <fstream>
#include <stdlib.h>
#include "VM.h"


char* readFileToBuffer(std::string filename)
{
    std::ifstream file;
    file.open(filename, std::ios::binary);
    file.seekg(0, std::ios::end);
    auto size = file.tellg();
    file.seekg(0, std::ios::beg);
    size -= file.tellg();
    char* buffer = new char[size];
    file.read(buffer, size);
    file.close();
    return buffer;
}

int main(int argc, char *argv[])
{

    if (argc < 2)
    {
        std::cout << "ERROR: no input file\n";
        return 1;
    }


    while (argc > 2)
    {
        int i = atoi(argv[argc-1]);
        SdasVM::stack.push_back(i);
        argc--;
    }

    std::string filename = argv[1];
    char* script = readFileToBuffer(filename);

    SdasVM vm(script);

    while (!vm.Done())
    {
        vm.Tick();
        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }

    return 0;
}
