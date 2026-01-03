#include "utils.h"
#include <iostream>

int transform(int input) {
    int result = input * 2;
    #ifdef DEBUG_MODE
        DEBUG_PRINT("Transform: " << input << " -> " << result);
    #endif
    return result;
}

int filter(int value) {
    #ifdef DEBUG_MODE
        DEBUG_PRINT("Filter: " << value);
    #endif
    
    if (value > 10) {
        return value;
    } else {
        return 0;
    }
}

