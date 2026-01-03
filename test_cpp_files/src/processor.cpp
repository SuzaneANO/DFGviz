#include "processor.h"
#include "utils.h"
#include <iostream>

DataProcessor::DataProcessor() : calc(nullptr), accumulator(0) {
    calc = new Calculator(0);
}

DataProcessor::~DataProcessor() {
    delete calc;
}

void DataProcessor::process(int value) {
    int transformed = transform(value);
    int filtered = filter(transformed);
    
    accumulator = accumulator + filtered;
    calc->add(filtered);
}

int DataProcessor::getResult() const {
    return calc->getValue();
}

void DataProcessor::reset() {
    accumulator = 0;
    delete calc;
    calc = new Calculator(0);
}

