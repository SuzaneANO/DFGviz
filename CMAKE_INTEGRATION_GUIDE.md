# CMake Integration Guide for C++ Analysis

## Overview

The CMake integration allows DFGviz to analyze C++ code using the exact compilation context from CMakeLists.txt. This ensures accurate path-sensitive analysis, proper header file resolution, and correct understanding of preprocessor defines.

## Quick Start

### 1. Basic Usage

```python
from cmake_parser import CMakeParser
from clang_complete_dataflow import ClangDataflowAnalyzer

# Parse CMakeLists.txt
cmake_path = Path("CMakeLists.txt")
parser = CMakeParser(cmake_path)

# Get compile arguments for a source file
source_file = Path("src/main.cpp")
compile_args = parser.get_compile_args(source_file)

# Analyze with CMake context
analyzer = ClangDataflowAnalyzer(str(source_file), compile_args=compile_args)
success = analyzer.analyze_with_clang()

if success:
    # Access analysis results
    print(f"Found {len(analyzer.defined_functions)} functions")
    print(f"Found {len(analyzer.defined_classes)} classes")
    print(f"Found {len(analyzer.dataflow_edges)} dataflow edges")
```

### 2. Convenience Function

```python
from cmake_parser import parse_cmake_for_analysis

compile_args = parse_cmake_for_analysis(
    cmake_path=Path("CMakeLists.txt"),
    source_file=Path("src/main.cpp")
)

analyzer = ClangDataflowAnalyzer(str(source_file), compile_args=compile_args)
analyzer.analyze_with_clang()
```

## What CMake Integration Provides

### ✅ Include Path Resolution
CMake knows where headers are located. The parser extracts:
- `include_directories()` → `-I` flags
- `target_include_directories()` → `-I` flags
- Resolves `${CMAKE_SOURCE_DIR}` and other variables

### ✅ Preprocessor Definitions
Path-sensitive analysis requires knowing which `#ifdef` blocks are active:
- `add_definitions(-DDEBUG_MODE)` → `-DDEBUG_MODE` flag
- `target_compile_definitions()` → `-D` flags
- Enables accurate analysis of conditional compilation

### ✅ C++ Standard Version
Ensures Clang uses the correct C++ standard:
- `set(CMAKE_CXX_STANDARD 17)` → `-std=c++17` flag
- Respects project's C++ version requirements

### ✅ Source/Header File Discovery
Parses file lists from CMake:
- `set(SOURCES ...)` → List of source files
- `set(HEADERS ...)` → List of header files
- Enables multi-file analysis

## Example: Path-Sensitive Analysis

Consider this code with `DEBUG_MODE` define:

```cpp
// main.cpp
int main() {
    int x = 10;
    
    #ifdef DEBUG_MODE
        int debug_value = x * 2;  // Only compiled if DEBUG_MODE defined
        x = debug_value;
    #endif
    
    return x;
}
```

**Without CMake**: Analysis might miss `debug_value` if `DEBUG_MODE` isn't defined.

**With CMake**: 
1. CMakeLists.txt has `add_definitions(-DDEBUG_MODE)`
2. Parser extracts `-DDEBUG_MODE`
3. Clang analyzes with `DEBUG_MODE` defined
4. `debug_value` is detected and dataflow `x → debug_value → x` is tracked

## Supported CMake Commands

### Parsed Commands
- ✅ `include_directories()`
- ✅ `add_definitions()`
- ✅ `set(CMAKE_CXX_STANDARD ...)`
- ✅ `set(SOURCES ...)`
- ✅ `set(HEADERS ...)`
- ✅ `target_include_directories()`
- ✅ `target_compile_definitions()`

### CMake Variables Resolved
- `${CMAKE_SOURCE_DIR}` → Project root directory
- `${CMAKE_CURRENT_SOURCE_DIR}` → Current directory
- `${CMAKE_CURRENT_LIST_DIR}` → Directory of current CMakeLists.txt

## Testing

Run the CMake analysis test suite:

```bash
python test_cmake_analysis.py
```

Tests verify:
- ✅ CMakeLists.txt parsing
- ✅ Compile argument generation
- ✅ Analysis with CMake settings
- ✅ Header file resolution
- ✅ Path-sensitive analysis
- ✅ Interprocedural analysis

## Integration with DFGviz GUI

The CMake integration can be used in the DFGviz GUI:

1. Select a C++ project with CMakeLists.txt
2. The analyzer will automatically detect and parse CMakeLists.txt
3. Analysis uses exact compilation context from CMake
4. Path-sensitive analysis works correctly with preprocessor defines

## Benefits

1. **Accuracy**: Uses exact compilation context
2. **Real-world**: Works with actual CMake projects
3. **Path-sensitive**: Understands conditional compilation
4. **Header-aware**: Properly resolves includes
5. **Multi-file**: Analyzes entire projects correctly

## Limitations

- Standard library paths may need manual configuration
- Complex CMake logic (macros, functions) may not be fully parsed
- Requires CMakeLists.txt to be present

## Future Enhancements

- Automatic standard library path detection
- Support for CMake generator expressions
- Integration with CMake build system for live analysis
- Support for CMake cache variables

