# pragma once

#include <string>
#include <unordered_map>

struct point{
    int x;
    int y;
};

std::unordered_map<wchar_t, int> count_chars(std::wstring _);
int from_factors(std::unordered_map<int, int> _);
bool did_john_escape(std::unordered_map<std::string, point> _);
void components(point origin, std::unordered_map<int, point>& _);