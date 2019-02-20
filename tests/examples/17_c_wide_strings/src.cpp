#include "src.h"
#include <string.h>
#include <wchar.h>
#include <iostream>

using namespace std;

bool any_upper(wchar_t const * in){
    while (*in){
        if ((*in >= 'A') && (*in <= 'Z'))
            return true;
        in++;
    }
    return false;
}
wchar_t* big_string(int max){
    auto out = new wchar_t[max+1];
    out[max] = '\0';
    for (int i = 0; i<max; i++){
        out[i] = '0'+(i%10);
    }
    return out;
}
void small_string(wchar_t** out){
    *out = L"little old me";
}
void str_mul(wchar_t const* in, int n, wchar_t *& out){
    auto batch_size = wcslen(in);
    out = new wchar_t[batch_size*n+1];
    for (int i = 0; i < n; i++){
        for (int j = 0; j < batch_size; j++){
            out[i*batch_size + j] = in[j];
        }
    }
    out[batch_size*n] = '\0';
}
wchar_t* hebrew(){
    auto ret =
    L"שלום"
    ;
    return (wchar_t*)ret;
}
void get_null(wchar_t*& SF_out){
    SF_out = nullptr;
}