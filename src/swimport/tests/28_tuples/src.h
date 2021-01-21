# pragma once

#include <string>
#include <tuple>
#include <vector>
#include <utility>

struct point{
    int x;
    int y;
};

struct person{
    int id;
    int age;
};

std::string repeat(std::tuple<char, int> _);
std::tuple<char, int> first_lowercase(std::string _);

std::vector<std::tuple<person, wchar_t const *, point>> personnel();

bool is_ok(std::tuple<person, wchar_t const *, point> _);

std::pair<int, int> factors(int base);

std::tuple<> empty();
std::tuple<std::tuple<>> wrap();