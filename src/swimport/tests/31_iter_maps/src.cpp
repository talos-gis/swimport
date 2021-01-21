#include "src.h"
#include <iostream>
#include <cstdio>
#define PY_PRINT(preamble, o) wcout << preamble; PyObject_Print(o, stdout, 0); wcout << endl;
using namespace std;
#include <cmath>

std::unordered_map<wchar_t, int> count_chars(std::wstring str){
    std::unordered_map<wchar_t, int> ret;
    for (const wchar_t c: str){
        if (!ret.insert({c,1}).second)
            ret[c]++;
    }
    return ret;
}
int from_factors(std::unordered_map<int, int> factors){
    int ret = 1;
    for (auto pair: factors){
        ret *= (int)(pow(pair.first, pair.second));
    }
    return ret;
}
bool did_john_escape(std::unordered_map<std::string, point> places){
    auto john = places.find("john");
    return john == places.end() ||
        abs(john->second.x) >= 10 || abs(john->second.y) >= 10;
}
void components(point origin, std::unordered_map<int, point>& out){
    out.insert({0,{origin.x, 0}});
    out.insert({1,{0, origin.y}});
}