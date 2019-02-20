#include "src.h"

#include <stdexcept>
#include <iostream>
#include <fstream>
#include <cerrno>
#include <system_error>

int factorial(int i){
    if (!i)
        return 1;
    return factorial(i-1)*i;
}
double inv(double x){
    return 1.0/x;
}
int sign(int x){
    if (x == 5)
        return 5;
    if (x < 0)
        return -1;
    return x > 0;
}
