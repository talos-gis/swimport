#include "src.h"

unsigned char crc(unsigned char const* B_in, size_t len){
    int ret = 0;
    for (auto i = 0; i < len; i++){
        ret += (unsigned short int)B_in[i];
        ret %= 256;
    }
    return (unsigned char)ret;
}
void big_bytes(size_t max, unsigned char** BF_out, size_t* len){
    *BF_out = new unsigned char[max];
    *len = max;
    for (auto i = 0; i< max; i++){
        (*BF_out)[i] = (unsigned char)(i%256);
    }
}
void bytes_mul(unsigned char const* B_in, size_t in_len, size_t mul_by, unsigned char *&BF_out, size_t& out_len){
    out_len = in_len * mul_by;
    BF_out = new unsigned char[out_len];
    for (size_t i = 0; i < mul_by; i++){
        for (size_t j = 0; j < in_len; j++){
            BF_out[j+i*in_len] = B_in[j];
        }
    }
}
