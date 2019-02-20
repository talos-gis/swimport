#include "src.h"
#include <string.h>
#include <stdlib.h>

int sum(int const * A_members, size_t n){
    auto ret = 0;
    for (int i = 0; i < n; i++){
        ret += *A_members;
        A_members++;
    }
    return ret;
}
void digits(int n, int** A_output, size_t* size, int base){
    auto ret = (int*)malloc(0);
    size_t i = 0;
    while (n != 0){
        ret = (int*)realloc(ret, sizeof(int)*(++i));
        ret[i-1] = n%base;
        n /= base;
    }
    *size = i;
    *A_output = ret;
}
void inc(double * AIO_x, size_t n, double offset){
    for (size_t i = 0; i < n; i++){
        AIO_x[i] += offset;
    }
}


const int VERY_BIG_NUMBER = 1'000'000;

void very_big_array(int** A_out, size_t* size){
    *A_out = new int[VERY_BIG_NUMBER];
    *size = VERY_BIG_NUMBER;
}

void very_big_array_malloc(int** A_out, size_t* size){
    *A_out = (int*)calloc(VERY_BIG_NUMBER, sizeof(int));
    *size = VERY_BIG_NUMBER;
}

int vbav[1000] = {};

void very_big_array_view(int*& A_out, size_t& size){
    A_out = vbav;
    size = 1000;
}