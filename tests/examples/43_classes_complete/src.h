# pragma once
#include <map>
#include <string>

class Polynomial{
private:
    int * orders;
    double * coffs;
    int nom_count;
    Polynomial(std::map<int,double> coffs);
public:
    Polynomial();
    Polynomial(double scalar);
    Polynomial(double coff, int order);
    Polynomial(Polynomial const & rhs);
    ~Polynomial();

    Polynomial& operator=(Polynomial const& rhs);
    Polynomial operator+(Polynomial const& rhs) const;
    Polynomial operator-(Polynomial const& rhs) const;
    Polynomial operator*(Polynomial const& rhs) const;
    Polynomial operator-() const;

    double operator()(double x) const;
    static const Polynomial x;
};

