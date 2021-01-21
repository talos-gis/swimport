#include "src.h"

int fibonacci(int index)
{
	if (index == 0)
	    return 0;
	if (index == 1)
	    return 1;
	return fibonacci(index-1) + fibonacci(index-2);
}

int divmod(int a, int b, int* remainder)
{
	*remainder = a%b;
	return a/b;
}

// demonstrate the None ignoring quirk
int* choose(bool returnNull, int* willBeFive){
    *willBeFive = 5;
    if (returnNull)
        return nullptr;
    return new int(0);
}