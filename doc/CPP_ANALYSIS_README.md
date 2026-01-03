# C++ Dataflow Analysis with Clang

This directory contains a C++ version of DFGviz that uses Clang/LLVM for static analysis of C++ code.

## Overview

The C++ analyzer (`clang_complete_dataflow.py`) provides the same functionality as the Python version (`scalpel_complete_dataflow.py`) but for C++ code:

- **Variable-to-variable dataflow tracking**
- **Path-sensitive analysis** using Clang's CFG
- **Interprocedural analysis** across function boundaries
- **Class and method analysis** for C++ OOP features
- **Interactive visualizations** (same D3.js frontend)

## Requirements

### System Requirements

1. **Clang/LLVM** - Must be installed on your system
   - **Windows**: 
     - **Chocolatey (Admin required)**: `choco install llvm -y` (run PowerShell as Administrator)
     - **Manual**: Download from [LLVM releases](https://github.com/llvm/llvm-project/releases)
     - **winget**: `winget install LLVM.LLVM` (Windows 11/10)
   - **Linux**: `sudo apt-get install clang libclang-dev` (Ubuntu/Debian) or `sudo yum install clang-devel` (RHEL/CentOS)
   - **macOS**: `brew install llvm` or comes with Xcode

2. **Python Clang Bindings**
   ```bash
   pip install clang
   ```

3. **Set LIBCLANG_PATH** (if needed)
   - **Windows**: `set LIBCLANG_PATH=C:\Program Files\LLVM\bin\libclang.dll`
   - **Linux**: `export LIBCLANG_PATH=/usr/lib/x86_64-linux-gnu/libclang.so.1`
   - **macOS**: `export LIBCLANG_PATH=/usr/local/opt/llvm/lib/libclang.dylib`

### Python Dependencies

```bash
pip install clang>=16.0.0
```

## Usage

### Basic Analysis

```bash
python clang_complete_dataflow.py --file example.cpp
```

### With Include Paths

```bash
python clang_complete_dataflow.py --file example.cpp --include /usr/include/c++/11 --include /usr/local/include
```

### Analyze Specific Function

```bash
python clang_complete_dataflow.py --file example.cpp --function main
```

### Specify C++ Standard

```bash
python clang_complete_dataflow.py --file example.cpp --std c++20
```

## Example

Analyze the test file:

```bash
cd dataflow_analysis
python clang_complete_dataflow.py --file test_example.cpp
```

This will generate:
- `test_example_dataflow.json` - Complete dataflow analysis
- `dataflow_graph.html` - Interactive visualization (if HTML generation is enabled)

## How It Works

### Clang Integration

The analyzer uses Clang's Python bindings (`clang.cindex`) to:

1. **Parse C++ source** - Clang parses the file into an AST
2. **Traverse AST** - Recursively visit nodes (functions, classes, statements)
3. **Extract CFG** - Clang provides control flow graph information
4. **Track Dataflow** - Analyze variable definitions, uses, and assignments
5. **Build Graph** - Create dataflow edges between variables

### Key Differences from Python Version

| Feature | Python (Scalpel) | C++ (Clang) |
|---------|------------------|-------------|
| **Parser** | Scalpel CFG | Clang AST |
| **CFG Access** | Direct CFG nodes | AST traversal + Clang CFG |
| **Type System** | Dynamic | Static (strong typing) |
| **OOP Support** | Classes, methods | Classes, structs, methods, templates |
| **Build System** | None needed | May need include paths |

### Supported C++ Features

- ✅ Variable declarations and assignments
- ✅ Function definitions and calls
- ✅ Class definitions and methods
- ✅ Control flow (if/else, while, for)
- ✅ Path-sensitive analysis
- ✅ Interprocedural analysis
- ✅ Member variable access
- ✅ Function parameters and return values

### Limitations

- ⚠️ **Templates**: Basic support, complex template metaprogramming may not be fully analyzed
- ⚠️ **Macros**: Preprocessor macros are expanded before analysis
- ⚠️ **Multiple Files**: Currently analyzes single files (header dependencies handled via includes)
- ⚠️ **Pointers/References**: Basic pointer analysis, advanced pointer aliasing not tracked

## Output Format

The JSON output follows the same format as the Python version for compatibility with existing visualization tools:

```json
{
  "metadata": {
    "analysis_method": "clang_cfg",
    "clang_available": true,
    "file": "example.cpp",
    "timestamp": "2024-01-01T12:00:00",
    "total_variables": 10,
    "total_definitions": 15,
    "total_uses": 20,
    "total_dataflow_edges": 12,
    "functions": ["main", "processData"],
    "classes": ["Calculator"]
  },
  "variable_definitions": {
    "x": [{"variable": "x", "location": {...}, "function": "main", ...}],
    ...
  },
  "variable_uses": {...},
  "dataflow_edges": {...},
  "call_graph": {...}
}
```

## Troubleshooting

### Clang Not Found

```
Warning: Clang Python bindings not available.
```

**Solution**: Install Clang and set `LIBCLANG_PATH` environment variable.

### Parse Errors

```
[ERROR] Failed to parse example.cpp
```

**Solution**: 
- Check that the file compiles with Clang
- Add necessary include paths with `--include`
- Ensure C++ standard is correct (`--std c++17`)

### Missing Headers

```
[WARNING] Clang reported X diagnostic(s)
```

**Solution**: Add include directories:
```bash
python clang_complete_dataflow.py --file example.cpp --include /usr/include/c++/11
```

## Integration with DFGviz

The C++ analyzer generates JSON in the same format as the Python analyzer, so:

- ✅ Same visualization frontend (D3.js)
- ✅ Same HTML generation (`generate_interactive_dataflow.py`)
- ✅ Same git history analysis (if extended)
- ✅ Compatible with existing tools

## Future Enhancements

Potential improvements:

1. **Multi-file Analysis** - Analyze entire projects with header dependencies
2. **Template Specialization** - Better template analysis
3. **Pointer Analysis** - Advanced pointer aliasing tracking
4. **CFG Visualization** - Direct Clang CFG visualization
5. **Build System Integration** - Auto-detect compile flags from CMake/Make

## References

- [Clang Python Bindings](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [LLVM Documentation](https://llvm.org/docs/)
- [Clang CFG](https://clang.llvm.org/doxygen/classclang_1_1CFG.html)

