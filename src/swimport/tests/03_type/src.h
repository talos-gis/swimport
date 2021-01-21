# pragma once

struct Point3D{
    double x,y,z;
};

double norm(Point3D point);
Point3D fromPolar(double phase, double radius = 1, double z = 0);
Point3D middle(Point3D const & point0, Point3D const * point1, double w0=1, double w1=1);
void components(Point3D const & point, Point3D* x, Point3D* y, Point3D* z);
// create a point from x,y,z. set it to out. return the sign of x,y,z's product. true=positive or zero, false=negative
bool mk_point(double x, double y, double z, Point3D* out);

void flip_xy(Point3D* IO_p);