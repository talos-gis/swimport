#include "src.h"

int sum(std::vector<int> ints){
    int ret = 0;
    for(int i: ints)
        ret += i;
    return ret;
}
size_t max_len(std::vector<wchar_t const *> i){
    size_t ret = 0;
    for (wchar_t const * s: i){
        auto len = wcslen(s);
        if (len > ret)
            ret = len;
    }
    return ret;
}
point agg(std::vector<point> i){
    auto retx = 0, rety = 0;
    for (auto const & p: i){
        retx += p.x;
        rety += p.y;
    }
    return {retx, rety};
}
int oldest_person_id(std::vector<person> i){
    auto ret = -1;
    auto max = 0;
    for (const person p: i){
        if (p.age > max){
            max = p.age;
            ret = p.id;
        }
    }
    return ret;
}
double sum_of_products(std::vector<std::deque<int>> iter){
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

std::vector<std::deque<float>> matrix(){
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