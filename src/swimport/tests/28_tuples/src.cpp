#include <string>
#include <cwchar>
#include <iostream>
	#include <cstdio>
	#define PY_PRINT(preamble, o) cout << preamble; PyObject_Print(o, stdout, 0); cout << endl;
	using namespace std;
#include "src.h"

std::string repeat(std::tuple<char, int> tuple){
    std::string ret;
    auto letter = std::get<0>(tuple);
    auto times = std::get<1>(tuple);
    for (int i = 0; i < times; i++)
        ret += letter;
    return ret;
}

std::tuple<char, int> first_lowercase(std::string str){
    for (auto i = 0; i < str.size(); i++){
        auto c = str[i];
        if (c <= 'z' && c >= 'a')
            return std::make_tuple(c, i);
    }
    return std::make_tuple('\0', -1);
}

std::vector<std::tuple<person, wchar_t const *, point>> personnel(){
    return {
        std::make_tuple<person, wchar_t const *, point>({0, 18}, (wchar_t const *)L"jim", {1,2}),
        std::make_tuple<person, wchar_t const *, point>({1, 27}, (wchar_t const *)L"dwight", {7,11}),
        std::make_tuple<person, wchar_t const *, point>({2, 30}, (wchar_t const *)L"mike", {55,100}),
    };
}
bool is_ok(std::tuple<person, wchar_t const *, point> obj){
    auto name = std::get<1>(obj);
    auto ret = wcsncmp(name, L"prison", 6) == 0;
    return ret;
}

std::pair<int, int> factors(int base){
    for (auto i = 2; i*i <= base; i++){
        if (base %i == 0)
            return std::make_pair(i, base/i);
    }
    return std::make_pair(1, base);
}

std::tuple<> empty(){
    return std::make_tuple();
}
std::tuple<std::tuple<>> wrap(){
    return std::make_tuple(empty());
}