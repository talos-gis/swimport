#include "src.h"

std::array<int,10> primes(){
    return {2,3,5,7,11,13,17,19,23,29};
}
std::array<std::pair<int,int>, 3> zip(std::array<int,3> a, std::array<int,3> b){
    return {
        std::make_pair(a[0], b[0]),
        std::make_pair(a[1], b[1]),
        std::make_pair(a[2], b[2])
    };
}