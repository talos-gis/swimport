#include "src.h"

byte mul(byte a, byte b){
    return a*b;
}
void div(byte a, byte b, byte* f, byte* r){
    *f = a/b;
    *r = a%b;
}
byte inc(byte const * a){
    return *a+1;
}

byte dec(byte const & a){
    return a-1;
}

void round(byte* IO_byte){
    *IO_byte = (*IO_byte) & ~1;
}