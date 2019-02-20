#include "src.h"
#include <cmath>

Point::Point(int x, int y): x(x), y(y){}

char Point::get_z(){
    return z;
}

void Point::set_z(char z){
    if (z >= 'a')
        z -= ('a'-'A');
    this->z = z;
}

void decompose(Point const& in, Point& out){
    out = {in.x, 0};
}

double Point::polar(double* radius){
    *radius = std::sqrt(x*x + y*y);
    return atan2(y,x);
}
std::vector<Point> Point::mirrors(){
    return {
        {-x,y},
        {-x,-y},
        {x,-y}
    };
}