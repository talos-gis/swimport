# pragma once

int mutate(int seed, bool inc);

char* is_ok(bool const* result);

int sum_of_digits(int seed, int base, bool& IO_overflow);

int sign(bool b);
int sign(int i);

bool is_even(int i);
bool is_even(bool const* b);

int foo(char const* s);
int foo(bool b);