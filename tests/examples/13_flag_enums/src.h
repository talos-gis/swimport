# pragma once
enum Color {BLACK = 0, RED = 1, BLUE = 2, YELLOW = 4, PURPLE = RED|BLUE, GREEN = BLUE|YELLOW, ORANGE = RED|YELLOW,
 WHITE = RED|YELLOW|BLUE};

bool is_primary(Color c);
bool is_composite(Color const* c);
bool contains(Color const &a, Color b);
Color complement(Color a);
bool triad(Color const *a, Color* out1, Color& out2);
void invert_color(Color* IO_color);