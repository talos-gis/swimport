#include "src.h"
#include <cmath>

Universe::Universe(): id(Universe::next_id){
    Universe::next_id++;
}
int Universe::get_id(){
    return this->id;
}

int Universe::next_id = 0;
int Universe::dimensions = 3;