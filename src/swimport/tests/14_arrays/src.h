# pragma once

int sum(int const * A_members, size_t n);
void digits(int n, int** A_output, size_t* size, int base = 10);
void inc(double * AIO_x, size_t n, double offset);
void very_big_array(int** AF_out, size_t* size);
void very_big_array_malloc(int** AF_out, size_t* size);

void very_big_array_view(int*& A_out, size_t& size);