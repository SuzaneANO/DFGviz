#ifndef CALCULATOR_H
#define CALCULATOR_H

class Calculator {
private:
    int value;
    int multiplier;
    
public:
    Calculator(int initial_value);
    void add(int x);
    void multiply(int x);
    int getValue() const;
    void setMultiplier(int m);
};

#endif // CALCULATOR_H

