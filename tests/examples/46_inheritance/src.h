#include <vector>
# pragma once

struct Shape{
    virtual bool Contains(int x, int y) = 0;
    virtual double x_min() = 0;
    virtual double y_min() = 0;
    virtual double x_max() = 0;
    virtual double y_max() = 0;
    virtual double area();
};

struct Circle: public Shape{
private:
    double x,y,r;
public:
    Circle(double x, double y, double r);
    double x_min();
    double y_min();
    double x_max();
    double y_max();
    bool Contains(int x, int y);
};

struct Rectangle: public Shape{
private:
    double x,y,w,h;
public:
    Rectangle(double x, double y, double w, double h);
    double x_min();
    double y_min();
    double x_max();
    double y_max();
    bool Contains(int x, int y);
    double area();
};