#include <string>

#include "src.h"

std::vector<int> fib(int max){
    auto ret = std::vector<int>{0,1};
    while (ret.back() < max){
        ret.push_back(ret.at(ret.size()-1) + ret.at(ret.size()-2));
    }
    return ret;
}

void digits(int o, std::vector<int>& out_iter){
    while (o){
        out_iter.push_back(o%10);
        o/=10;
    }
}

std::vector<char*> names(){
    return {"jim", "victor", "loa"};
}

std::vector<point> points(){
    return {{1,2},{2,3},{3,4}};
}

std::vector<std::vector<float>> matrix(){
    return {
        {1,2,3},
        {2,3,4},
        {3,4,5}
    };
}

std::vector<person> people(){
    return {
        {15, 20},
        {47, 98},
        {7, 3}
    };
}

std::vector<std::string> strings(){
    return {"jim", "victor", "loa"};
}