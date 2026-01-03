# Scalpel Dataflow and AST Analysis

This directory contains the essential code for analyzing dataflow and AST using scalpel.

## Core Files

### Analysis Scripts
- **`scalpel_complete_dataflow.py`** - Main script that analyzes all Python files and generates complete variable-to-variable dataflow JSON
  - Uses AST parsing to track variable definitions, uses, and dataflow edges
  - Outputs: `scalpel_complete_dataflow.json`

### Visualization Scripts
- **`generate_interactive_dataflow.py`** - Generates interactive HTML/SVG visualization of dataflow graph
  - Reads: `scalpel_complete_dataflow.json`
  - Outputs: `dataflow_graph.html`

- **`generate_ast_visualization.py`** - Generates interactive HTML/SVG visualization of AST tree structure
  - Parses Python files directly
  - Outputs: `ast_tree.html`

## Output Files

- **`scalpel_complete_dataflow.json`** - Complete variable-to-variable dataflow analysis
  - Contains all variable definitions, uses, and dataflow edges
  - Format: `{metadata, variables: {var_name: {definitions, uses, dataflow_outgoing, dataflow_incoming}}}`

- **`dataflow_graph.html`** - Interactive dataflow graph visualization
  - Zoom, pan, click nodes for details
  - Force-directed graph layout
  - Export as SVG

- **`ast_tree.html`** - Interactive AST tree visualization
  - Expand/collapse nodes
  - Hierarchical tree structure
  - Export as SVG

## Documentation

- **`scalpel_complete_dataflow_README.md`** - Detailed documentation of the dataflow analysis

## Usage

All scripts should be run from the `dataflow_analysis/` directory:

1. **Generate dataflow analysis:**
   ```bash
   cd dataflow_analysis
   python scalpel_complete_dataflow.py
   ```

2. **Generate dataflow visualization:**
   ```bash
   cd dataflow_analysis
   python generate_interactive_dataflow.py
   ```

3. **Generate AST visualization:**
   ```bash
   cd dataflow_analysis
   python generate_ast_visualization.py
   ```

4. **Open visualizations:**
   - Open `dataflow_analysis/dataflow_graph.html` in browser for dataflow graph
   - Open `dataflow_analysis/ast_tree.html` in browser for AST tree

## Note

The `scalpel_complete_dataflow.py` script currently uses AST parsing directly. Scalpel is imported but not actively used in the current implementation. The script can be enhanced to use Scalpel's CFGBuilder and DUC (Define-Use Chain) for more advanced analysis if needed.

