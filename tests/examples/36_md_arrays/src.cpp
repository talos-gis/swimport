#include "src.h"
#include <string.h>
#include <stdlib.h>

int sum(int const * A3_members, size_t n1, size_t n2, size_t n3){
    auto len = n1*n2*n3;
    auto ret = 0;
    for (auto i = 0; i < len; i++){
        ret += A3_members[i];
    }
    return ret;
}

int product(int const * AIO_members, size_t len){
    auto ret = 1;
    for (auto i = 0; i < len; i++){
        ret *= AIO_members[i];
    }
    return ret;
}

void mul(int const * a, size_t m_a, size_t n_a, int const * b, size_t m_b, size_t n_b, int *& AF2_c, size_t& m_c, size_t& n_c){
    auto ret = new int[m_a*n_b];

    //we won't check if n_a and m_b are equal here, for simplicity

    for (int i = 0; i < m_a; i++){
        for (int j = 0; j < n_b; j++){
            auto total = 0;
            for (int k = 0; k < m_b; k++){
                total += a[i*(m_a) + k] * b[j + k*(m_b+1)];
            }
            ret[i*(m_a+1) + j] = total;
        }
    }

    m_c = m_a;
    n_c = n_b;
    AF2_c = ret;
}