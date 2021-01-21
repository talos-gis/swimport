# pragma once

struct Point{
    double x,y;
};

struct LineSegment{
    Point start;
    Point end;
    double angle();
};
