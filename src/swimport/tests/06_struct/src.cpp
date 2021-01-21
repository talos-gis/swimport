#include "src.h"
#include <cmath>

Point Point_Create(int x, int y){
    return {x,y};
}
double Point_Radius(Point const * p){
    return std::sqrt(p->x*p->x + p->y*p->y);
}
int Point_Hamilton(Point p){
    return std::abs(p.x) + std::abs(p.y) ;
}
void Point_Components(Point const& p, Point* x, Point* y){
    *x = {p.x, 0};
    *y = {0, p.y};
}
void Point_Inc(Point* IO_point){
    *IO_point = {IO_point->x+1, IO_point->y+1};
}