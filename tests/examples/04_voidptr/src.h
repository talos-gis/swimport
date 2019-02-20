# pragma once

struct Point{
    double x,y;
};

void* point_create(double x, double y);
void point_destroy(void const* point);
double point_x(void const* point);
bool point_middle(void const * a, void const * b, void** out);