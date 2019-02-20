# pragma once

union Padded{
    int w;
    char n;
};

Padded Padded_Create(int w);
Padded Padded_Create(char n);

bool Padded_Trim(Padded const & p, Padded* out);

void Padded_Trim_Inplace(Padded *& IO_padded);