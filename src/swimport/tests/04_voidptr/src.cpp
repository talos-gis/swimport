#include "src.h"

void* point_create(double x, double y){
    auto ret = new Point();
    ret->x = x;
    ret->y = y;
    return ret;
}
void point_destroy(void const * point){
    delete (Point*)point;
}
double point_x(void const * point){
    return ((Point*)point)->x;
}
bool point_middle(void const * a, void const * b, void** out){
    *out = new Point();
    (*(Point**)out)->x = (((Point*)a)->x+((Point*)b)->x)/2;
    (*(Point**)out)->y = (((Point*)a)->y+((Point*)b)->y)/2;
    return true;
}
