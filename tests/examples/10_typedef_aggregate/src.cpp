#include "src.h"

nint mk(int x){
    return x;
}
int extract(nint p){
    return p;
}
nint sum(nint const & p1, nint p2){
    return mk(extract(p1) + extract(p2));
}
void div(nint const * p1, nint p2, nint* f, nint* r){
    *f = mk(extract(*p1) / extract(p2));
    *r = mk(extract(*p1) % extract(p2));
}