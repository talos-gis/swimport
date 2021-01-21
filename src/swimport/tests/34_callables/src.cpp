#include "src.h"
#include <iostream>
#include <math.h>
using namespace std;


void knock(std::function<void()> callback){
    callback();
}

double search(std::function<double(double)> cmp_func, double min, double max, double epsilon){
    while (1){
        auto mid = (min + max)/2;
        auto cmp = cmp_func(mid);
        if (fabs(cmp) < epsilon)
            return mid;
        if (cmp > 0)
            max = mid;
        else
            min = mid;
    }
}

void report_romans(std::function<bool(int,std::string)> report){
    report(1, "I")
        && report(2, "II")
        && report(3, "III")
        && report(4, "IV")
        && report(5, "V")
        && report(6, "VI")
        && report(7, "VII")
        && report(8, "VIII")
        && report(9, "IX")
        && report(10, "X");
}