#include "src.h"
#include <cmath>



Point Point_Create(int x, int y){
    return {x, y};
}

void decompose(Point const& in, Point& out){
    out = {in.x, 0};
}