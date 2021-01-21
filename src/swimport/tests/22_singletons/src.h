# pragma once

# include "../resources/py_singletons.h"

int fib(int index, int zero, int one);
int fib(int index, int one);
int fib(int index, ellipsis);

bool accept_only_notimplemented(NotImplementedType);

int count(char const * haystack, char needle, int startindex, int endindex);
int count(char const * haystack, char needle, int startindex, NoneType);
int count(char const * haystack, char needle, NoneType, int endindex);
int count(char const * haystack, char needle, NoneType, NoneType);

ellipsis get_ellipsis();
NoneType get_none();
NotImplementedType get_ni();

char* code(int s);
char* code(PySingleton);

PySingleton from_code(char const *);
