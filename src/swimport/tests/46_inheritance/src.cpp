#include "src.h"
#include <cmath>
#include <random>

const int sample_size = 10'000'000;

double Shape::area(){
    std::random_device rd;
    std::mt19937 gen(rd());
    double xn = x_min(), xx = x_max(), yn = y_min(), yx = y_max();
    std::uniform_real_distribution<double> x_rand(xn, xx), y_rand(yn, yx);
    int points_in = 0;
    for (int i = 0; i < sample_size; i++){
        auto x = x_rand(gen);
        auto y = y_rand(gen);
        if (Contains(x,y))
            points_in++;
    }
    return (points_in / (double)sample_size) * ((xx-xn) * (yx - yn));
}

Circle::Circle(double x, double y, double r): x(x), y(y), r(r){}
double Circle::x_min(){
    return x-r;
}
double Circle::y_min(){
    return y-r;
}
double Circle::x_max(){
    return x+r;
}
double Circle::y_max(){
    return y+r;
}
bool Circle::Contains(int x, int y){
    return (std::pow(x-this->x, 2) + std::pow(y-this->y, 2)) < r*r;
}

Rectangle::Rectangle(double x, double y, double w, double h): x(x), y(y), w(w), h(h){}
double Rectangle::x_min(){
    return x;
}
double Rectangle::y_min(){
    return y;
}
double Rectangle::x_max(){
    return x+w;
}
double Rectangle::y_max(){
    return y+h;
}
bool Rectangle::Contains(int x, int y){
    x -= this->x;
    y -= this->y;
    return x > 0 && x < w && y > 0 && y < h;
}
double Rectangle::area(){
    return h*w;
}