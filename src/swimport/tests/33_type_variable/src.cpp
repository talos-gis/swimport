#include "src.h"
#include <cmath>

Point2D origin = {0,0};
std::vector<Point2D> corners = {};

const Point2D zero = {0,0};

int count_corners(){
    return corners.size();
}
double mag_origin(){
    return origin.x*origin.x + origin.y*origin.y;
}