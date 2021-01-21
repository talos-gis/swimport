#include "src.h"

int sum(std::unordered_set<int> ints){
    int ret = 0;
    for(int i: ints)
        ret += i;
    return ret;
}
size_t max_len(std::unordered_set<wchar_t const *> i){
    size_t ret = 0;
    for (wchar_t const * s: i){
        auto len = wcslen(s);
        if (len > ret)
            ret = len;
    }
    return ret;
}
double sum_of_products(std::vector<std::unordered_set<int>> iter){
    double ret = 0;
    for (auto seq: iter){
        double prod = 1;
        for (auto i: seq){
            prod *= i;
        }
        ret += prod;
    }
    return ret;
}

void digits(int o, std::unordered_set<int>& out_iter){
    while (o){
        out_iter.insert(o%10);
        o/=10;
    }
}

std::unordered_set<char*> names(){
    return {"jim", "victor", "loa"};
}

std::vector<std::unordered_set<float>> matrix(){
    return {
        {1,2,3},
        {2,3,4},
        {3,4,5}
    };
}

std::unordered_set<std::string> strings(){
    return {"jim", "victor", "loa"};
}