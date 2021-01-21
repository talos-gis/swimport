#include "src.h"
#include <iostream>

bool in_slice(slice<int, int, int> slice, int item){
    if (slice.has_step && slice.step < 0){
        if ((slice.has_start && slice.start < item)
        || (slice.has_end && slice.end >= item))
            return false;
        return (item - slice.start) % slice.step == 0;
    }
    if ((slice.has_start && slice.start > item)
        || (slice.has_end && slice.end <= item))
        return false;
    return (!slice.has_step) || ((item - slice.start) % slice.step) == 0;
}
bool in_continuum(slice<double, double> slice, double item){
    return (!slice.has_start || slice.start <= item)
        && (!slice.has_end || slice.end > item);
}
slice<double, double> join_continuum(slice<double, double> s1, slice<double, double> s2){
    return {s1.start, s1.has_start, s2.end, s2.has_end};
}