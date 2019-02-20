# pragma once
#include <map>
#include <string>
#include <vector>

struct Polynomial{
private:
    std::map<int, double> coefficients;
public:
    Polynomial();
    Polynomial(double scalar);
    Polynomial(double coff, int order);
    Polynomial(Polynomial const & rhs);

    Polynomial operator+(Polynomial const& rhs) const;
    Polynomial operator-(Polynomial const& rhs) const;
    Polynomial operator*(Polynomial const& rhs) const;
    Polynomial operator-() const;

    double operator()(double x) const;

    std::string __str__() const;

    static Polynomial from_coefficients(std::vector<double> coffs_inc);
};

extern const Polynomial x;