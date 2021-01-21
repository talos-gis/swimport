#include "src.h"
#include <cmath>

double norm(Point3D point){
    return std::sqrt(point.x*point.x + point.y*point.y + point.z*point.z);
}

Point3D fromPolar(double phase, double radius, double z){
    return {std::cos(phase) * radius, std::sin(phase) * radius, z};
}

Point3D middle(Point3D const & point0, Point3D const * point1, double w0, double w1){
    auto s = w0+w1;
    return {
        (point0.x*w0 + point1->x*w1)/s,
        (point0.y*w0 + point1->y*w1)/s,
        (point0.z*w0 + point1->z*w1)/s,
    };
}

void components(Point3D const & point, Point3D* x, Point3D* y, Point3D* z){
    *x = {point.x,0,0};
    *y = {0,point.y,0};
    *z = {0,0,point.z};
}

bool mk_point(double x, double y, double z, Point3D* out){
    *out = {x,y,z};
    auto prod = x*y*z;
    return (prod >= 0);
}

void flip_xy(Point3D* IO_p){
    *IO_p = {IO_p->y, IO_p->x, IO_p->z};
}