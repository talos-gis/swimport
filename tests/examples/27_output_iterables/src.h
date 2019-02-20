# pragma once

#include <vector>

std::vector<int> fib(int max);

void digits(int o, std::vector<int>& out_iter);

std::vector<char*> names();

struct point{
    int x;
    int y;
};

std::vector<point> points();

std::vector<std::vector<float>> matrix();

struct person{
    int id;
    int age;
};

std::vector<person> people();

std::vector<std::string> strings();