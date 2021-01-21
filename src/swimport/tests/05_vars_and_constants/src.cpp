#include "src.h"

const double pi = 3.14;
const double tau = pi*2;

bool error_occurred = false;
int mood = 0;

int factorial(int i){
    if (i < 0){
        error_occurred = true;
        return 0;
    }
    auto ret = i;
    while (--i){
        ret *= i;
    }
    return ret;
}

void resetError(){
    error_occurred = false;
}

int getMood(){
    return mood;
}

int taste = 0;
int scent = 5;

void inc_scent(){
    scent++;
}