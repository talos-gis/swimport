#include "src.h"

bool is_primary(Color c){
    return (c == RED) || (c == BLUE) || (c == YELLOW);
}
bool is_composite(Color const* c){
    return (*c == GREEN) || (*c == PURPLE) || (*c == ORANGE);
}
bool contains(Color const &a, Color b){
    return (b&a) == b;
}
Color complement(Color a){
    return (Color)(WHITE & ~a);
}

bool triad(Color const *a, Color* out1, Color& out2){
    if ((*a == WHITE) || (*a == BLACK)){
        out2 = *out1 = *a;
        return false;
    }
    if (*a == RED){
        *out1 = PURPLE;
        out2 = ORANGE;
    }
    else if (*a == BLUE){
        *out1 = PURPLE;
        out2 = GREEN;
    }
    else if (*a == YELLOW){
        *out1 = ORANGE;
        out2 = GREEN;
    }
    else if (*a == PURPLE){
        *out1 = BLUE;
        out2 = RED;
    }
    else if (*a == ORANGE){
        *out1 = YELLOW;
        out2 = RED;
    }
    else if (*a == GREEN){
        *out1 = BLUE;
        out2 = YELLOW;
    }
    return true;
}
void invert_color(Color* IO_color){
    *IO_color = (Color)(WHITE & ~(*IO_color));
}