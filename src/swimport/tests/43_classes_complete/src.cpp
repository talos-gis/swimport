#include "src.h"
#include <cmath>

using coff_map = std::map<int,double>;

Polynomial::Polynomial(std::map<int,double> coff_map): nom_count(coff_map.size()){
    orders= new int[nom_count];
    coffs = new double[nom_count];
    int i = 0;
    for (auto pair: coff_map){
        orders[i] = pair.first;
        coffs[i] = pair.second;
        i++;
    }
}

Polynomial::Polynomial():nom_count(0), orders(nullptr), coffs(nullptr){}
Polynomial::Polynomial(double scalar):Polynomial(scalar, 0){}
Polynomial::Polynomial(double coff, int order): nom_count(1), orders(new int[1] {order}), coffs(new double[1] {coff}){}
Polynomial::Polynomial(Polynomial const & rhs): nom_count(rhs.nom_count){
    orders= new int[nom_count];
    coffs = new double[nom_count];
    std::copy(rhs.orders, rhs.orders+nom_count, orders);
    std::copy(rhs.coffs, rhs.coffs+nom_count, coffs);
}
Polynomial::~Polynomial(){
    if (coffs)
        delete[] coffs;
    if (orders)
        delete[] orders;
}

Polynomial& Polynomial::operator=(Polynomial const& rhs){
    if (&rhs == this)
        return *this;

    if (rhs.nom_count != nom_count){
        if (coffs)
            delete[] coffs;
        if (orders)
            delete[] orders;
        nom_count = rhs.nom_count;
        orders = new int[nom_count];
        coffs = new double[nom_count];
    }
    std::copy(rhs.orders, rhs.orders+nom_count, orders);
    std::copy(rhs.coffs, rhs.coffs+nom_count, coffs);
    return *this;
}
Polynomial Polynomial::operator+(Polynomial const& rhs) const{
    coff_map cm;
    for (int i=0; i < nom_count; i++){
        cm[orders[i]] = coffs[i];
    }

    for (int j=0; j < rhs.nom_count; j++){
        auto found = cm.find(rhs.orders[j]);
        if (found == cm.end())
            cm[rhs.orders[j]] = rhs.coffs[j];
        else
            found->second += rhs.coffs[j];
    }
    return {cm};
}
Polynomial Polynomial::operator-(Polynomial const& rhs) const{
    return this->operator+(-rhs);
}
Polynomial Polynomial::operator*(Polynomial const& rhs) const{
    coff_map cm;
    for (int i=0; i < nom_count; i++){
        for (int j=0; j < rhs.nom_count; j++){
            auto coff = coffs[i] * rhs.coffs[j];
            auto key = orders[i] + rhs.orders[j];

            auto found = cm.find(key);

            if (found == cm.end())
                cm[key] = coff;
            else
                found->second += coff;
        }
    }
    return {cm};
}
Polynomial Polynomial::operator-() const{
    return this->operator*(-1);
}

double Polynomial::operator()(double x) const{
    double ret = 0;
    for (int i=0; i < nom_count; i++){
        auto mem = coffs[i] * pow(x, orders[i]);
        ret += mem;
    }
    return ret;
}

const Polynomial Polynomial::x = Polynomial(1,1);