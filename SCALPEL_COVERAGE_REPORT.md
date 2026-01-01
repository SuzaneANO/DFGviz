# Scalpel Coverage Analysis Report for DFGviz

## Summary

**Overall Coverage: ~4% of Scalpel codebase**

DFGviz uses only a small subset of Scalpel's functionality, focusing primarily on CFG (Control Flow Graph) building and basic MNode operations.

## Scalpel Modules Used

### ✅ Used Modules (Partial Coverage)

1. **`scalpel.cfg.builder`** - **17% coverage**
   - Used for: Building CFGs from Python files
   - Key usage: `CFGBuilder().build(name, tree)`
   - Coverage: 59/350 statements

2. **`scalpel.cfg.model`** - **24% coverage**
   - Used for: CFG node and graph models
   - Key usage: Accessing `cfg.nodes`, `cfg.functions`, `node.statements`
   - Coverage: 36/148 statements

3. **`scalpel.core.mnode`** - **15% coverage**
   - Used for: MNode parsing and analysis
   - Key usage: `MNode(filepath)`, `parse_func_defs()`, `gen_cfg()`, `parse_vars()`, `parse_func_calls()`
   - Coverage: 25/164 statements

4. **`scalpel.core.func_call_visitor`** - **17% coverage**
   - Used for: Function call tracking
   - Coverage: 29/170 statements

5. **`scalpel.core.util`** - **21% coverage**
   - Used for: Utility functions
   - Coverage: 29/138 statements

6. **`scalpel.core.vars_visitor`** - **22% coverage**
   - Used for: Variable tracking
   - Coverage: 32/143 statements

### ❌ Unused Modules (0% Coverage)

The following Scalpel modules are **not used at all** by DFGviz:

1. **`scalpel.SSA`** (0% coverage)
   - Static Single Assignment analysis
   - All SSA-related files: `alg.py`, `const.py`, `def_use.py`, `ssa.py`
   - **Total: 589 statements unused**

2. **`scalpel.pycg`** (0% coverage)
   - Program Call Graph generation
   - All pycg modules: `pycg.py`, `machinery/*`, `processing/*`, `formats/*`
   - **Total: ~2000+ statements unused**

3. **`scalpel.typeinfer`** (0% coverage)
   - Type inference analysis
   - All typeinfer modules: `analysers.py`, `classes.py`, `typeinfer.py`, `utilities.py`, `visitors.py`
   - **Total: ~1454 statements unused**

4. **`scalpel.import_graph`** (0% coverage)
   - Import graph analysis
   - **Total: 137 statements unused**

5. **`scalpel.rewriter`** (0% coverage)
   - Code rewriting functionality
   - **Total: 276 statements unused**

6. **`scalpel.scope_graph`** (0% coverage)
   - Scope graph analysis
   - **Total: 153 statements unused**

7. **`scalpel.dataflow.IFDS`** (0% coverage)
   - IFDS (Interprocedural, Finite, Distributive, Subset) dataflow analysis
   - **Total: 13 statements unused**

8. **`scalpel.core._scope_graph`** (0% coverage)
   - Internal scope graph implementation
   - **Total: 153 statements unused**

9. **Other unused core modules:**
   - `scalpel.core.class_hierarchy` (0%)
   - `scalpel.core.class_visitor` (0%)
   - `scalpel.core.fun_def_visitor` (0%)
   - `scalpel.core.kw_visitor` (0%)
   - `scalpel.core.source_visitor` (0%)

## Detailed Usage Patterns

### How DFGviz Uses Scalpel

1. **MNode Initialization**
   ```python
   from scalpel.core.mnode import MNode
   mnode = MNode(filepath)
   ```

2. **Function/Class Definition Parsing**
   ```python
   func_defs = mnode.parse_func_defs()
   ```

3. **CFG Generation**
   ```python
   from scalpel.cfg import CFGBuilder
   cfg = mnode.gen_cfg()  # Primary method
   # Fallback:
   builder = CFGBuilder()
   func_cfg = builder.build(node.name, node)
   ```

4. **Variable Parsing**
   ```python
   vars_info = mnode.parse_vars()
   ```

5. **Function Call Parsing**
   ```python
   func_calls = mnode.parse_func_calls()
   ```

6. **CFG Node Traversal**
   ```python
   for cfg_node in cfg.nodes:
       for stmt in cfg_node.statements:
           # Analyze statements
   ```

## Coverage Statistics

| Module Category | Statements | Covered | Coverage % |
|----------------|------------|---------|------------|
| **CFG Building** | 498 | 95 | 19% |
| **MNode Core** | 164 | 25 | 15% |
| **Visitors** | 329 | 61 | 19% |
| **SSA** | 589 | 0 | 0% |
| **Call Graph (pycg)** | ~2000 | 0 | 0% |
| **Type Inference** | ~1454 | 0 | 0% |
| **Other** | ~675 | 0 | 0% |
| **TOTAL** | **5727** | **214** | **~4%** |

## Key Findings

### ✅ What DFGviz Uses
- **CFG Building**: Core functionality for building control flow graphs
- **MNode Parsing**: Function definitions, variables, function calls
- **Basic CFG Traversal**: Accessing nodes and statements
- **Path-Sensitive Analysis**: Using CFG structure for path tracking

### ❌ What DFGviz Doesn't Use
- **SSA (Static Single Assignment)**: Advanced dataflow analysis
- **Call Graph Generation**: Program-wide call graph analysis
- **Type Inference**: Type analysis capabilities
- **Code Rewriting**: Code transformation features
- **Import Analysis**: Module dependency tracking
- **Scope Graph**: Advanced scope analysis

## Implications

### Performance
- DFGviz only loads ~4% of Scalpel's codebase
- Most unused modules are never imported or executed
- This is actually **efficient** - only what's needed is used

### Dependencies
- DFGviz could potentially use a lighter-weight version of Scalpel
- However, Scalpel is designed as a complete framework, so this is expected

### Future Enhancements
If DFGviz wanted to expand functionality, it could leverage:
- **SSA**: For more precise dataflow analysis
- **Type Inference**: For better variable type tracking
- **Call Graph**: For interprocedural call analysis
- **Import Graph**: For cross-module analysis

## Conclusion

DFGviz uses Scalpel **efficiently** by focusing on its core CFG building capabilities. The 4% coverage is expected and appropriate for the tool's use case. DFGviz doesn't need the advanced features like SSA, type inference, or call graph generation - it builds its own custom dataflow analysis on top of Scalpel's CFG foundation.

**Recommendation**: The current usage is optimal for DFGviz's requirements. No changes needed.

---

*Report generated by: `test_scalpel_coverage.py`*  
*Date: 2026-01-01*  
*Scalpel Version: python-scalpel>=0.1.0*

