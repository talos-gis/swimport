# pragma once

extern const double pi;
extern const double tau;
const int one = 1;

extern bool error_occurred;

int factorial(int i);
void resetError();

extern int mood;

int getMood();

extern int taste;
extern int scent;

void inc_scent();