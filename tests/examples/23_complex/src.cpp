#include "src.h"

#include <cmath>

double radius(std::complex<double> c){
    return std::abs(c);
}
std::complex<double> root(int i){
    double PI = std::acos(-1);
    return std::exp((PI * std::complex<double>(0,2)) / (double)i);
}
void complements(std::complex<double> const & a, std::complex<double>* b, std::complex<double>& c){
    *b = {a.real(), 0};
    c = {0, a.imag()};
}
