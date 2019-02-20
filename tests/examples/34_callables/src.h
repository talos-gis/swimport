# pragma once

#include <functional>
#include <tuple>
#include <string>

void knock(std::function<void()> _);

double search(std::function<double(double)> _, double min, double max, double epsilon = 1e-9);

void report_romans(std::function<bool(int,std::string)> _);