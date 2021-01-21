# pragma once

struct Point3D{
    double x,y,z;
};

double norm(Point3D const * point);
Point3D neg(Point3D const & point);