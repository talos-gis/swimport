#include "src.h"

bool any_upper(std::string in){
    for (auto it=in.begin(); it!=in.end(); ++it){
        if ((*it >= 'A') && (*it <= 'Z'))
            return true;
    }
    return false;
}
std::string big_string(int max){
    std::string out;
    out.reserve(max);
    for (int i = 0; i<max; i++){
        out += ('0'+(i%10));
    }
    return out;
}
void small_string(std::string* out){
    *out = "little old me";
}
void str_mul(std::string in, int n, std::string& out){
    auto batch_size = in.size();
    out = "";
    out.reserve(batch_size * n);
    for (int i = 0; i < n; i++){
        out += in;
    }
}