#include "src.h"
#include <string.h>
#include <iostream>

using namespace std;

bool any_upper(char const * in){
    while (*in){
        if ((*in >= 'A') && (*in <= 'Z'))
            return true;
        in++;
    }
    return false;
}
char* big_string(int max){
    auto out = new char[max+1];
    out[max] = '\0';
    for (int i = 0; i<max; i++){
        out[i] = '0'+(i%10);
    }
    return out;
}
void small_string(char** out){
    *out = "little old me";
}
void str_mul(char const* in, int n, char*& out){
    auto batch_size = strlen(in);
    out = new char[batch_size*n+1];
    for (int i = 0; i < n; i++){
        for (int j = 0; j < batch_size; j++){
            out[i*batch_size + j] = in[j];
        }
    }
    out[batch_size*n] = '\0';
}
void get_null(char*& SF_out){
    SF_out = nullptr;
}