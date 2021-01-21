# pragma once

struct Point{
    int x, y;
};

Point Point_Create(int x, int y);
double Point_Radius(Point const * p);
int Point_Hamilton(Point p);
void Point_Components(Point const& p, Point* x, Point* y);
void Point_Inc(Point* IO_point);
