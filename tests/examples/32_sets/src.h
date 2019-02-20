# pragma once

#include <string>
#include <unordered_set>

int sum(std::unordered_set<int>);
size_t max_len(std::unordered_set<wchar_t const *>);

void digits(int o, std::unordered_set<int>& out_iter);

double sum_of_products(std::vector<std::unordered_set<int>>);

std::unordered_set<char*> names();

std::vector<std::unordered_set<float>> matrix();

std::unordered_set<std::string> strings();