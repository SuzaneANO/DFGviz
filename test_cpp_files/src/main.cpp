#include "processor.h"
#include "utils.h"
#include <iostream>
#include <vector>

#ifdef DEBUG_MODE
    #include <cassert>
#endif

int main() {
    int input = 10;
    
    // Path-sensitive: DEBUG_MODE affects behavior
    #ifdef DEBUG_MODE
        DEBUG_PRINT("Starting in debug mode");
        int debug_value = input * 2;
        input = debug_value;
    #endif
    
    DataProcessor processor;
    
    // Process multiple values
    std::vector<int> values = {5, 10, 15, 20};
    for (int val : values) {
        int processed = transform(val);
        processor.process(processed);
    }
    
    int result = processor.getResult();
    
    #ifdef DEBUG_MODE
        DEBUG_PRINT("Final result: " << result);
        assert(result > 0);
    #endif
    
    std::cout << "Result: " << result << std::endl;
    
    return 0;
}

