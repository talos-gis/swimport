# pragma once

#include <string>
#include <vector>
#include <deque>

int sum(std::vector<int>);
size_t max_len(std::vector<wchar_t const *>);
struct point{
    int x;
    int y;
};
point agg(std::vector<point>);
struct person{
    int id;
    int age;
};
int oldest_person_id(std::vector<person>);

double sum_of_products(std::vector<std::deque<int>>);

std::vector<int> fib(int max);

void digits(int o, std::vector<int>& out_iter);

std::vector<char*> names();
std::vector<point> points();

std::vector<std::deque<float>> matrix();

std::vector<person> people();

std::vector<std::string> strings();