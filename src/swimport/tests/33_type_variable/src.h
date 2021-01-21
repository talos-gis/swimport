# pragma once
#include <vector>

struct Point2D{
    double x,y;
};

extern Point2D origin;
extern std::vector<Point2D> corners;

extern const Point2D zero;

int count_corners();
double mag_origin();