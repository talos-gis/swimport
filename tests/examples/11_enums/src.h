# pragma once

enum Flavor {SWEET, SOUR, BITTER=5, SALTY, UMAMI=-1};

bool good_flavor(Flavor f);
bool is_made_up(Flavor const * f);
Flavor opposite(Flavor const & f);
int get_made_up(Flavor* out);
void invert(Flavor* IO_flavor);

enum Color {BLACK = 0, RED = 1, BLUE = 2, YELLOW = 4, PURPLE = RED|BLUE, GREEN = BLUE|YELLOW, ORANGE = RED|YELLOW,
 WHITE = RED|YELLOW|BLUE};

bool is_primary(Color c);
bool is_composite(Color const* c);
bool contains(Color const &a, Color b);
Color complement(Color a);
bool triad(Color const *a, Color* out1, Color& out2);
void invert_color(Color* IO_color);