#ifndef PROCESSOR_H
#define PROCESSOR_H

#include "calculator.h"

class DataProcessor {
private:
    Calculator* calc;
    int accumulator;
    
public:
    DataProcessor();
    ~DataProcessor();
    void process(int value);
    int getResult() const;
    void reset();
};

#endif // PROCESSOR_H

