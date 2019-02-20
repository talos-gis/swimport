#include "src.h"

Padded Padded_Create(int w){
    return {w};
}
Padded Padded_Create(char n){
    Padded ret;
    ret.w = 0;
    ret.n = n;
    return ret;
}
bool Padded_Trim(Padded const & p, Padded* out){
    if (p.w != p.n){
        *out = Padded_Create(p.n);
        return false;
    }
    *out = p;
    return true;
}

void Padded_Trim_Inplace(Padded *& IO_padded){
    IO_padded->w = IO_padded->n;
}