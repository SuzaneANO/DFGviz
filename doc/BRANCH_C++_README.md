# C++ Branch - Complete Prototype

## 🎉 What's New

This branch (`C++`) contains a **complete working prototype** of DFGviz for C++ code analysis!

## 📁 New Files

### Core Implementation
- **`clang_complete_dataflow.py`** - Main C++ analyzer (900+ lines)
  - Uses Clang/LLVM Python bindings
  - Analyzes C++ AST for dataflow
  - Generates JSON compatible with existing visualizations

### Test Files
- **`test_example.cpp`** - Example C++ code demonstrating various features
- **`test_clang_analysis.py`** - Test suite for verifying Clang setup

### Documentation
- **`CPP_ANALYSIS_README.md`** - Comprehensive documentation (installation, usage, troubleshooting)
- **`CPP_QUICK_START.md`** - 5-minute quick start guide
- **`CPP_PROTOTYPE_SUMMARY.md`** - Technical implementation summary

### Updated Files
- **`requirements.txt`** - Added `clang>=16.0.0` dependency
- **`README.md`** - Added note about C++ support

## 🚀 Quick Start

### 1. Install Clang

**Windows:**
```powershell
choco install llvm
set LIBCLANG_PATH=C:\Program Files\LLVM\bin\libclang.dll
```

**Linux:**
```bash
sudo apt-get install clang libclang-dev
export LIBCLANG_PATH=/usr/lib/x86_64-linux-gnu/libclang.so.1
```

**macOS:**
```bash
brew install llvm
export LIBCLANG_PATH=/usr/local/opt/llvm/lib/libclang.dylib
```

### 2. Install Python Bindings

```bash
pip install clang
```

### 3. Test It

```bash
cd dataflow_analysis
python clang_complete_dataflow.py --file test_example.cpp
```

## ✨ Features

### ✅ Implemented

- Variable-to-variable dataflow tracking
- Path-sensitive analysis (if/else, loops)
- Interprocedural analysis (function calls)
- Class and method analysis
- Control flow tracking
- JSON output (compatible with existing visualizations)
- HTML visualization (reuses D3.js frontend)

### 📊 Output

The analyzer generates:
- `*_dataflow.json` - Complete dataflow analysis
- `dataflow_graph.html` - Interactive visualization

## 🔧 Usage Examples

```bash
# Basic analysis
python clang_complete_dataflow.py --file example.cpp

# With include paths
python clang_complete_dataflow.py --file example.cpp --include /usr/include/c++/11

# Specific function only
python clang_complete_dataflow.py --file example.cpp --function main

# C++20 standard
python clang_complete_dataflow.py --file example.cpp --std c++20
```

## 📚 Documentation

- **[CPP_QUICK_START.md](CPP_QUICK_START.md)** - Get started in 5 minutes
- **[CPP_ANALYSIS_README.md](CPP_ANALYSIS_README.md)** - Full documentation
- **[CPP_PROTOTYPE_SUMMARY.md](CPP_PROTOTYPE_SUMMARY.md)** - Technical details

## 🧪 Testing

Run the test suite:

```bash
python test_clang_analysis.py
```

## 🎯 Architecture

The C++ analyzer mirrors the Python version:

| Component | Python | C++ |
|-----------|--------|-----|
| **Parser** | Scalpel CFG | Clang AST |
| **Analysis** | AST traversal | AST traversal |
| **Output** | JSON | JSON (same format) |
| **Visualization** | D3.js | D3.js (reused) |

## 🔄 Compatibility

- ✅ Same JSON format as Python version
- ✅ Works with existing `generate_interactive_dataflow.py`
- ✅ Compatible with existing visualization frontend
- ✅ Same CLI interface pattern

## ⚠️ Requirements

- Clang/LLVM installed on system
- `LIBCLANG_PATH` environment variable set
- Python `clang` package installed

## 🎓 Next Steps

1. **Test with your C++ code** - Try analyzing your own projects
2. **Report issues** - Let us know if you encounter problems
3. **Suggest features** - What C++ features should we add?

## 📝 Notes

- This is a **prototype** - fully functional but may have limitations
- Templates, advanced pointers, and multi-file analysis are partially supported
- The analyzer focuses on single-file analysis (headers via includes)

## 🙏 Credits

Built using:
- **Clang/LLVM** - Industry-standard C++ compiler infrastructure
- **Python Clang Bindings** - `clang` package for Python integration
- **DFGviz Framework** - Reuses visualization and JSON format from Python version

---

**Ready to analyze C++ code?** Start with [CPP_QUICK_START.md](CPP_QUICK_START.md)!


