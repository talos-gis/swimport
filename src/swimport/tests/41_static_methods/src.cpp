#include "src.h"
#include <cmath>
#include <sstream>

Polynomial::Polynomial():coefficients(){}
Polynomial::Polynomial(double scalar):Polynomial(scalar, 0){}
Polynomial::Polynomial(double coff, int order): Polynomial(){
    coefficients[order] = coff;
}
Polynomial::Polynomial(Polynomial const & rhs):coefficients(rhs.coefficients){}

Polynomial Polynomial::operator+(Polynomial const& rhs) const{
    auto ret = Polynomial(*this);
    for (auto pair: rhs.coefficients){
        auto found = ret.coefficients.find(pair.first);
        if (found == ret.coefficients.end())
            ret.coefficients[pair.first] = pair.second;
        else
            found->second += pair.second;
    }
    return ret;
}
Polynomial Polynomial::operator-(Polynomial const& rhs) const{
    return *this + (-rhs);
}
Polynomial Polynomial::operator*(Polynomial const& rhs) const{
    auto ret = Polynomial();
    for (auto pair1: this->coefficients){
        for (auto pair2: rhs.coefficients){
            auto coff = pair1.second * pair2.second;
            auto key = pair1.first + pair2.first;

            auto found = ret.coefficients.find(key);

            if (found == ret.coefficients.end())
                ret.coefficients[key] = coff;
            else
                found->second += coff;
        }
    }
    return ret;
}
Polynomial Polynomial::operator-() const{
    return *this * (-1);
}

double Polynomial::operator()(double x) const{
    double ret = 0;
    for (auto pair: coefficients){
        auto mem = pair.second * pow(x, pair.first);
        ret += mem;
    }
    return ret;
}

std::string Polynomial::__str__() const{
    std::string ret = "";
    for (auto pair: coefficients){
        std::ostringstream strs;
        strs << pair.second;
        auto coff = strs.str();

        std::ostringstream strs2;
        strs2 << pair.first;
        auto pow = strs2.str();
        ret += coff+"*x^"+std::string(pow)+"+";
    }
    return ret;
}
Polynomial Polynomial::from_coefficients(std::vector<double> coffs_inc){
    Polynomial ret;
    int pow = 0;
    for (auto c: coffs_inc){
        ret = ret + Polynomial(c, pow++);
    }
    return ret;
}

const Polynomial x = Polynomial(1,1);