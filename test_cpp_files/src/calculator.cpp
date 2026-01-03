#include "calculator.h"
#include <iostream>

Calculator::Calculator(int initial_value) : value(initial_value), multiplier(1) {
}

void Calculator::add(int x) {
    value = value + x;
}

void Calculator::multiply(int x) {
    value = value * multiplier;
    multiplier = x;
}

int Calculator::getValue() const {
    return value;
}

void Calculator::setMultiplier(int m) {
    multiplier = m;
}

