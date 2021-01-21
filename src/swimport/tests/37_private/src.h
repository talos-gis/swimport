# pragma once

struct Point{
    int x, y;
    Point(): Point(0,0){}
    Point(int x, int y): x(x), y(y){}
 private:
    char z;
};

Point Point_Create(int x, int y);
void decompose(Point const& in, Point& out);
