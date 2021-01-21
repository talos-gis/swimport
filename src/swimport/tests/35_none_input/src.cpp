#include "src.h"
#include <cmath>

double norm(Point3D const * point){
    if (!point)
        return -1;
    return std::sqrt(point->x*point->x + point->y*point->y + point->z*point->z);
}

Point3D neg(Point3D const & point){
    return {point.x, point.y, -point.z};
}