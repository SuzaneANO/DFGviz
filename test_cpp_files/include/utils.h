#ifndef UTILS_H
#define UTILS_H

#ifdef DEBUG_MODE
    #define DEBUG_PRINT(x) std::cout << "[DEBUG] " << x << std::endl
#else
    #define DEBUG_PRINT(x)
#endif

int transform(int input);
int filter(int value);

#endif // UTILS_H

