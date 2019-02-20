#include "src.h"
#include <string.h>
#include <stdlib.h>

void chars_upper(char const * s, char** AF_out, size_t& n){
    auto ret = new char[strlen(s)];
    size_t i = 0;
    while (*s != 0){
        char c = *s;
        s++;
        if (c <= 'z' && c >= 'a')
            c += 'A'-'a';
        ret[i] = c;
        i++;
    }
    n = i;
    *AF_out = ret;
}
bool chars_anylower(char const * A_arr, size_t n){
    for (size_t i = 0; i < n; i++){
        char c = *A_arr;
        if (c <= 'z' && c >= 'a')
            return true;
        A_arr++;
    }
    return false;
}