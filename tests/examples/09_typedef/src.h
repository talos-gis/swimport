# pragma once

typedef unsigned char byte;

byte mul(byte a, byte b);
void div(byte a, byte b, byte* f, byte* r);
byte inc(byte const * a);
byte dec(byte const & a);
void round(byte* IO_byte);