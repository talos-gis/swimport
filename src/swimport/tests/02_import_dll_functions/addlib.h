#pragma once

#ifdef ADDLIB_EXPORTS  
#define ADDLIB_API __declspec(dllexport)   
#else  
#define ADDLIB_API __declspec(dllimport)   
#endif  

extern "C" {
    ADDLIB_API int add(int a, int b);
}