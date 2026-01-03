# C++ Dataflow Analysis Test Suite

Comprehensive test suite for the C++ dataflow analysis functionality using Clang/LLVM.

## Overview

This test suite covers various aspects of C++ code analysis:

- **Basic Tests**: Variable definitions, assignments, arithmetic expressions
- **Function Tests**: Function calls, interprocedural analysis, nested calls
- **Class Tests**: Class definitions, methods, OOP features
- **Control Flow Tests**: If/else statements, while loops, for loops
- **Edge Cases**: Error handling, invalid syntax, empty files
- **Complex Scenarios**: Real-world code patterns, nested structures

## Requirements

### Prerequisites

1. **Clang/LLVM** must be installed
   - Windows: `choco install llvm` or download from [LLVM releases](https://github.com/llvm/llvm-project/releases)
   - Linux: `sudo apt-get install clang libclang-dev`
   - macOS: `brew install llvm`

2. **Python Clang Bindings**
   ```bash
   pip install clang
   ```

3. **Set LIBCLANG_PATH** (if needed)
   - Windows: `set LIBCLANG_PATH=C:\Program Files\LLVM\bin\libclang.dll`
   - Linux: `export LIBCLANG_PATH=/usr/lib/x86_64-linux-gnu/libclang.so.1`
   - macOS: `export LIBCLANG_PATH=/usr/local/opt/llvm/lib/libclang.dylib`

## Running Tests

### Option 1: Run All Tests

```bash
cd dataflow_analysis
python test_cpp_runner.py --all
```

### Option 2: Run Comprehensive Test Suite

```bash
python test_cpp_runner.py --comprehensive
```

Or directly:

```bash
python test_cpp_dataflow_comprehensive.py
```

### Option 3: Run Basic Tests

```bash
python test_cpp_runner.py --basic
```

Or directly:

```bash
python test_clang_analysis.py
```

### Option 4: Run Specific Test File

```bash
python test_cpp_runner.py --file test_cpp_dataflow_comprehensive.py
```

### Option 5: Using unittest

```bash
python -m unittest test_cpp_dataflow_comprehensive
```

### Option 6: Using pytest (if installed)

```bash
pytest test_cpp_dataflow_comprehensive.py -v
```

## Test Structure

### Test Files

- **`test_cpp_dataflow_comprehensive.py`**: Main comprehensive test suite
- **`test_clang_analysis.py`**: Basic Clang availability and parsing tests
- **`test_cpp_runner.py`**: Test runner with multiple options

### Test C++ Files

Located in `test_cpp_files/`:

- **`test_basic.cpp`**: Basic variable assignments and arithmetic
- **`test_functions.cpp`**: Function calls and interprocedural analysis
- **`test_classes.cpp`**: Class methods and OOP features
- **`test_control_flow.cpp`**: Control flow structures (if/else, loops)
- **`test_complex.cpp`**: Complex real-world scenarios

## Test Classes

### TestCPPDataflowBasic
Tests basic dataflow analysis:
- Simple variable assignments
- Multiple assignments
- Arithmetic expressions

### TestCPPFunctionCalls
Tests function-related analysis:
- Function calls with parameters
- Nested function calls
- Call graph construction

### TestCPPClasses
Tests OOP features:
- Class definitions
- Method calls
- Class attributes

### TestCPPControlFlow
Tests control flow structures:
- If/else statements
- While loops
- For loops

### TestCPPEdgeCases
Tests edge cases and error handling:
- Empty files
- Files with only comments
- Invalid syntax handling
- Standard library usage

### TestCPPComplexScenarios
Tests complex scenarios:
- Complex dataflow chains
- Nested classes
- Real-world code patterns

## Expected Output

When tests pass, you should see:

```
======================================================================
Comprehensive C++ Dataflow Analysis Test Suite
======================================================================

test_simple_variable_assignment (__main__.TestCPPDataflowBasic) ... ok
test_multiple_assignments (__main__.TestCPPDataflowBasic) ... ok
...

----------------------------------------------------------------------
Ran X tests in Y.YYYs

OK
[OK] All tests passed!
```

## Troubleshooting

### Clang Not Available

If you see `[WARNING] Clang not available`, check:

1. Clang is installed: `clang --version`
2. Python bindings installed: `pip install clang`
3. LIBCLANG_PATH is set correctly

### Parse Errors

Some tests may fail if:
- Clang cannot parse the C++ code (syntax errors)
- Include paths are missing
- C++ standard version mismatch

### Import Errors

If you get import errors:
- Make sure you're running from the `dataflow_analysis` directory
- Check that `clang_complete_dataflow.py` is in the same directory

## Adding New Tests

To add new tests:

1. Add a new test method to the appropriate test class in `test_cpp_dataflow_comprehensive.py`
2. Create a test C++ file in `test_cpp_files/` if needed
3. Follow the existing test patterns:
   - Use `setUp()` and `tearDown()` for fixtures
   - Use `create_test_file()` to create temporary test files
   - Use `assertIn()`, `assertTrue()`, etc. for assertions

Example:

```python
def test_my_feature(self):
    """Test description."""
    code = """
    int main() {
        // Your test code
    }
    """
    test_file = self.create_test_file(code)
    analyzer = ClangDataflowAnalyzer(str(test_file))
    success = analyzer.analyze_with_clang()
    
    self.assertTrue(success)
    # Add your assertions
```

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run C++ tests
  run: |
    cd dataflow_analysis
    python test_cpp_runner.py --all
```

## Coverage

To check test coverage (if coverage.py is installed):

```bash
coverage run --source=. test_cpp_dataflow_comprehensive.py
coverage report
coverage html  # Generate HTML report
```

## Contributing

When adding new features to `clang_complete_dataflow.py`, please:

1. Add corresponding tests
2. Ensure all tests pass
3. Update this README if needed

