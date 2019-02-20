#include <vector>
# pragma once

struct Point{
    int x, y;
    Point(int x, int y);
    char get_z();
    void set_z(char z);
    double polar(double* radius);
    std::vector<Point> mirrors();
 private:
    char z;
};

void decompose(Point const& in, Point& out);
