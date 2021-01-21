#include <vector>
# pragma once

class Universe{
    int id;
public:
    Universe();
    static const int meaning = 42;
    int get_id();
    static int next_id;
    static int dimensions;
};
