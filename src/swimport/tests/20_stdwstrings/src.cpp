#include "src.h"

bool any_upper(std::wstring in){
    for (auto it=in.begin(); it!=in.end(); ++it){
        if ((*it >= 'A') && (*it <= 'Z'))
            return true;
    }
    return false;
}
std::wstring big_string(int max){
    std::wstring out;
    out.reserve(max);
    for (int i = 0; i<max; i++){
        out += ('0'+(i%10));
    }
    return out;
}
void small_string(std::wstring* out){
    *out = L"little old me";
}
void str_mul(std::wstring in, int n, std::wstring& out){
    auto batch_size = in.size();
    out = L"";
    out.reserve(batch_size * n);
    for (int i = 0; i < n; i++){
        out += in;
    }
}
std::wstring hebrew(){
    return L"שלום";
}