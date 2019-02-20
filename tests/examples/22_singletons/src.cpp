#include "src.h"
#include <cstring>

#include <iostream>
using namespace std;

int fib(int index, int zero, int one){
    if (index == 0)
        return zero;
    while (index){
        int temp = zero;
        zero = one;
        one += temp;
        index--;
    }
    return zero;
}
int fib(int index, int one){
    return fib(index, 0 , one);
}
int fib(int index, ellipsis){
    return fib(index, 1);
}

bool accept_only_notimplemented(NotImplementedType){
    return true;
}

int count(char const * haystack, char needle, int startindex, int endindex){
    auto ret = 0;
    for (; startindex < endindex; startindex++){
        if (haystack[startindex] == needle)
            ret++;
    }
    return ret;
}
int count(char const * haystack, char needle, int startindex, NoneType){
    auto ret = 0;
    haystack += startindex;
    while (*haystack)
    {
        if (*haystack == needle)
            ret++;
        haystack++;
    }
    return ret;
}
int count(char const * haystack, char needle, NoneType, int endindex){
    return count(haystack, needle, 0, endindex);
}
int count(char const * haystack, char needle, NoneType, NoneType){
    return count(haystack, needle, 0, None);
}

ellipsis get_ellipsis(){
    return Ellipsis;
}
NoneType get_none(){
    return None;
}
NotImplementedType get_ni(){
    return None; // if the return type is a specific singleton, teh actual return value doesn't matter
}

char* code(int s){
    return nullptr;
}
char* code(PySingleton s){
    if (s == None)
        return "n";
    if (s == Ellipsis)
        return "...";
    if (s == NotImplemented)
        return "ni";
    return nullptr;
}

PySingleton from_code(char const * c){
    if (strcmp(c, "n") == 0)
        return None;
    if (strcmp(c, "ni") == 0)
        return NotImplemented;
    if (strcmp(c, "...") == 0)
        return Ellipsis;
    return None;
}