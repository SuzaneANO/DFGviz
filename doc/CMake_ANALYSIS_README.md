# CMake-Based C++ Analysis

This module provides CMakeLists.txt parsing and integration for accurate C++ dataflow analysis.

## Overview

The CMake-based analysis system:
1. **Parses CMakeLists.txt** to extract compilation settings
2. **Extracts include paths** for proper header file resolution
3. **Extracts preprocessor definitions** for path-sensitive analysis
4. **Determines C++ standard** version
5. **Configures Clang** with exact compilation context

## Features

### ✅ CMakeLists.txt Parsing
- Parses `include_directories()` commands
- Extracts `add_definitions()` and `target_compile_definitions()`
- Reads `CMAKE_CXX_STANDARD` setting
- Parses `set(SOURCES ...)` and `set(HEADERS ...)` lists
- Supports `target_include_directories()` for modern CMake

### ✅ Path-Sensitive Analysis
- Uses preprocessor definitions from CMake (e.g., `DEBUG_MODE`)
- Analyzes `#ifdef` blocks correctly based on actual compilation flags
- Understands conditional compilation paths

### ✅ Header File Support
- Resolves header includes using CMake include directories
- Analyzes class definitions in header files
- Tracks interprocedural calls across source and header files

## Usage

### Basic Usage

```python
from cmake_parser import CMakeParser
from clang_complete_dataflow import ClangDataflowAnalyzer

# Parse CMakeLists.txt
cmake_path = Path("CMakeLists.txt")
parser = CMakeParser(cmake_path)

# Get compile arguments for a source file
source_file = Path("src/main.cpp")
compile_args = parser.get_compile_args(source_file)

# Analyze with CMake-derived settings
analyzer = ClangDataflowAnalyzer(str(source_file), compile_args=compile_args)
analyzer.analyze_with_clang()
```

### Convenience Function

```python
from cmake_parser import parse_cmake_for_analysis

compile_args = parse_cmake_for_analysis(
    cmake_path=Path("CMakeLists.txt"),
    source_file=Path("src/main.cpp")
)

analyzer = ClangDataflowAnalyzer(str(source_file), compile_args=compile_args)
analyzer.analyze_with_clang()
```

## Example CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(${CMAKE_SOURCE_DIR}/src)

# Compile definitions
add_definitions(-DDEBUG_MODE)
add_definitions(-DVERSION_MAJOR=1)

# Source files
set(SOURCES
    src/main.cpp
    src/calculator.cpp
)

add_executable(my_app ${SOURCES})
```

## Test Suite

Run the CMake analysis tests:

```bash
python test_cmake_analysis.py
```

The test suite includes:
- CMakeLists.txt parsing tests
- Compile argument generation tests
- Header file analysis tests
- Path-sensitive analysis with preprocessor defines
- Interprocedural analysis across multiple files

## How It Works

### 1. CMake Parsing
The `CMakeParser` class reads CMakeLists.txt and extracts:
- Include directories → `-I` flags for Clang
- Definitions → `-D` flags for Clang
- C++ standard → `-std=c++XX` flag
- Source/header file lists

### 2. Compile Argument Generation
Builds Clang-compatible arguments:
```python
[
    '-std=c++17',
    '-I/path/to/include',
    '-I/path/to/src',
    '-DDEBUG_MODE',
    '-DVERSION_MAJOR=1'
]
```

### 3. Clang Analysis
Passes these arguments to Clang, ensuring:
- Headers are found correctly
- Preprocessor defines are applied
- C++ standard is respected
- Path-sensitive analysis works correctly

## Benefits

1. **Accurate Analysis**: Uses exact compilation context from CMake
2. **Header Support**: Properly resolves includes and analyzes headers
3. **Path Sensitivity**: Understands `#ifdef` blocks based on actual defines
4. **Multi-file**: Analyzes entire project with correct context
5. **Real-world**: Works with actual CMake projects

## Limitations

- Requires CMakeLists.txt to be present
- Standard library paths may need manual configuration
- Complex CMake logic (macros, functions) may not be fully parsed

## Future Improvements

- Support for CMake cache variables
- Automatic standard library path detection
- Support for CMake generator expressions
- Integration with CMake build system for live analysis

