#include "src.h"
#include <cmath>

double LineSegment::angle(){
    return std::atan2(end.y - start.y, end.x - start.x);
}