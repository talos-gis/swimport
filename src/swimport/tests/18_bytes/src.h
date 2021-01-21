# pragma once

unsigned char crc(unsigned char const* B_in, size_t len);
void big_bytes(size_t max, unsigned char** BF_out, size_t* len);
void bytes_mul(unsigned char const* B_in, size_t len, size_t mul_by, unsigned char *&BF_out, size_t& out_len);
