# Dataflow Graph Diff Highlighting Feature

## Overview

This feature adds **git-based diff highlighting** to the dataflow visualization, allowing you to see exactly what changed between commits. The system automatically compares the current graph with the previous commit and highlights **function definition edges** (edges that represent function calls) that were added, modified, or removed.

## Quick Start

```bash
# 1. Make sure you have a git commit with the previous graph
cd dataflow_analysis

# 2. Generate the dataflow graph (automatically compares with previous commit)
python generate_interactive_dataflow.py

# 3. Open dataflow_graph.html in your browser to see the highlighted changes
```

**What you'll see:**
- Light green edges = New function definition edges
- Orange edges = Modified function definition edges  
- Purple edges = Deleted function definition edges
- Legend showing counts of each change type

## Features

### 1. Automatic Git Comparison
- **Compares current commit with previous commit**: The script automatically retrieves the previous version of the dataflow graph from git (HEAD or HEAD~1)
- **No manual configuration needed**: Works automatically when `enable_diff=True` (default)

### 2. Function Definition Edge Highlighting
- **Only highlights function definition edges**: Regular dataflow edges are not highlighted - only edges that represent function calls (edges with `called_function` property)
- **Three types of changes detected**:
  - **Added**: New function definition edges
  - **Modified**: Function definition edges where the called function changed
  - **Removed**: Function definition edges that no longer exist

### 3. Color Scheme
The following colors are used to highlight changes:

| Change Type | Color | Hex Code | Description |
|------------|-------|----------|-------------|
| **Added** | Light Green | `#90EE90` | New function definition edges |
| **Modified** | Orange | `#FFA500` | Function definition edges where the called function changed |
| **Deleted** | Purple | `#9370DB` | Function definition edges that were removed |

### 4. Propagation Across All HTML Files
- **Main graph** (`dataflow_graph.html`): Shows diff highlighting for all function definition edges
- **Function-specific pages**: Each function's dataflow page also shows diff highlighting for that function's edges
- **Consistent styling**: Same colors and animations across all generated HTML files

## How It Works

### Step 1: Git Comparison
```python
previous_html = get_previous_commit_html(output_file)
previous_nodes, previous_links = parse_nodes_and_links_from_html(previous_html)
```

The script:
1. Gets the git repository root
2. Retrieves the previous commit's HTML file using `git show HEAD:path/to/file.html`
3. Parses nodes and links from the previous HTML

### Step 2: Graph Comparison
```python
diff_info = compare_graphs(nodes, links, previous_nodes, previous_links)
```

The comparison:
- Identifies new, removed, and modified nodes
- Identifies new, removed, and modified links
- **Filters to only function definition edges** (links with `called_function` property)

### Step 3: Apply Diff Classes
```python
add_diff_classes_to_nodes_and_links(nodes, links, diff_info, only_function_definitions=True)
```

Each link gets a CSS class:
- `link-new`: Added function definition edges
- `link-modified`: Modified function definition edges
- `link-removed`: Deleted function definition edges
- `link-unchanged`: No change (or not a function definition edge)

### Step 4: CSS Styling
The CSS applies colors and animations:
- **Light green** (`#90EE90`) with pulsing animation for new edges
- **Orange** (`#FFA500`) with pulsing animation for modified edges
- **Purple** (`#9370DB`) with dashed line for removed edges

## Usage

### Basic Usage

**Generate dataflow graph with diff highlighting:**
```bash
cd dataflow_analysis
python generate_interactive_dataflow.py
```

This will:
1. Load the dataflow JSON file (`scalpel_complete_dataflow.json`)
2. Generate the interactive HTML graph
3. **Automatically compare with the previous commit** (if available)
4. **Highlight function definition edges** that changed (light green/orange/purple)
5. Show a legend with change counts
6. Generate function-specific pages with diff highlighting

**Output:**
- `dataflow_graph.html` - Main interactive graph with diff highlighting
- `function_dataflow_*.html` - Function-specific pages with diff highlighting

### Filter by File

**Show only changes from a specific file:**
```bash
python generate_interactive_dataflow.py --filter-file extract_and_analyze_image.py
```

**What this does:**
- Filters the diff to only show changes from variables/edges in that specific file
- Reduces noise from other files
- Useful when you only modified one file

**Example:**
```bash
# Only show changes from langchain_multimodal_ollama.py
python generate_interactive_dataflow.py --filter-file langchain_multimodal_ollama.py
```

### Complete Workflow Example

**Step 1: Make code changes**
```python
# In extract_and_analyze_image.py
def test_dataflow_example():
    a = 1
    b = a
    c = 2
    d = b + c
    return d
```

**Step 2: Commit your code changes**
```bash
git add extract_and_analyze_image.py
git commit -m "Add test dataflow example"
```

**Step 3: Generate initial dataflow graph (if not done)**
```bash
cd dataflow_analysis
python scalpel_complete_dataflow.py  # Generates JSON
python generate_interactive_dataflow.py  # Generates HTML
```

**Step 4: Commit the graph (to establish baseline)**
```bash
git add dataflow_analysis/dataflow_graph.html
git add dataflow_analysis/scalpel_complete_dataflow.json
git commit -m "Add initial dataflow graph"
```

**Step 5: Make more changes and regenerate**
```python
# Add more function calls or modify existing ones
def another_function():
    x = test_dataflow_example()  # New function definition edge
    return x
```

**Step 6: Regenerate and see the diff**
```bash
python scalpel_complete_dataflow.py
python generate_interactive_dataflow.py --filter-file extract_and_analyze_image.py
```

**Step 7: View the results**
- Open `dataflow_graph.html` in your browser
- Look for:
  - **Light green edges**: New function definition edges
  - **Orange edges**: Modified function definition edges
  - **Purple edges**: Deleted function definition edges
- Check the legend in the bottom-right for counts

### Disable Diff Highlighting

**Option 1: Command line (modify script)**
Edit `generate_interactive_dataflow.py` and change:
```python
if __name__ == '__main__':
    generate_interactive_svg(enable_diff=False)  # Disable diff
```

**Option 2: Programmatic usage**
```python
from generate_interactive_dataflow import generate_interactive_svg

# Disable diff highlighting
generate_interactive_svg(
    dataflow_file='scalpel_complete_dataflow.json',
    output_file='dataflow_graph.html',
    enable_diff=False
)
```

### Advanced Usage

**Generate without filtering:**
```bash
# Shows all changes across entire codebase
python generate_interactive_dataflow.py
```

**Generate with file filtering:**
```bash
# Shows only changes from specific file
python generate_interactive_dataflow.py --filter-file your_file.py
```

**View function-specific diff:**
1. Open `dataflow_graph.html`
2. Click on a function call edge (red edges are clickable)
3. This opens the function-specific page
4. The function page also shows diff highlighting for that function's edges

### Command Line Options

Currently supported:
- `--filter-file <filename>`: Filter diff to only show changes from specified file
  - Example: `--filter-file extract_and_analyze_image.py`
  - The filename should match the file path in your codebase

**Note:** The script automatically:
- Detects if you're in a git repository
- Retrieves the previous commit's graph
- Compares and highlights differences
- Generates all HTML files with diff highlighting

## Example Output

When you run the script, you'll see output like:

```
[INFO] Comparing with previous commit...
[INFO] Found previous version: 146 nodes, 232 links
[INFO] Function definition edges: 21 new, 16 modified, 0 removed
[OK] Interactive SVG visualization generated: dataflow_graph.html
```

## Visual Indicators

### In the Graph
- **Light green edges**: New function definition edges (pulsing animation)
- **Orange edges**: Modified function definition edges (pulsing animation)
- **Purple edges**: Deleted function definition edges (dashed, semi-transparent)
- **Legend box**: Shows counts of added/modified/deleted function edges

### Legend
The legend appears in the bottom-right corner of the graph and shows:
- **Added (X edges)**: Number of new function definition edges
- **Modified (X edges)**: Number of modified function definition edges
- **Deleted (X edges)**: Number of removed function definition edges

## Technical Details

### Function Definition Edges
A function definition edge is identified by having a `called_function` property. These edges represent dataflow through function calls, for example:

```python
# This creates a function definition edge:
result = some_function(variable)  # Edge: variable -> result (called_function: "some_function")
```

### Comparison Logic
1. **Node comparison**: Compares nodes by name and properties (total_flows, outgoing, incoming)
2. **Link comparison**: Compares links by source/target variable names and `called_function` property
3. **Filtering**: Only includes links that have `called_function` in the diff results

### Git Integration
- Uses `git rev-parse --show-toplevel` to find the repository root
- Uses `git show HEAD:path` to retrieve previous commit's file
- Falls back to `HEAD~1` if `HEAD` doesn't have the file
- Handles cases where the file doesn't exist in git history

## Files Modified

### `generate_interactive_dataflow.py`
- Added `get_previous_commit_html()`: Retrieves previous commit's HTML
- Added `parse_nodes_and_links_from_html()`: Extracts graph data from HTML
- Added `compare_graphs()`: Compares current and previous graphs
- Added `add_diff_classes_to_nodes_and_links()`: Applies diff classes with filtering
- Modified `generate_interactive_svg()`: Integrates diff comparison
- Modified `generate_function_dataflow_page()`: Adds diff support to function pages
- Added CSS styles for diff highlighting (light green, orange, purple)
- Added diff legend HTML generation

## Troubleshooting

### "No previous commit found"
- **Cause**: The HTML file doesn't exist in git history
- **Solution**: Commit the current graph first, then regenerate

### "Could not verify model availability"
- **Cause**: Git is not available or the file path is incorrect
- **Solution**: Ensure you're in a git repository and the file path is correct

### Too many changes shown
- **Cause**: Comparing against a very old commit
- **Solution**: Use `--filter-file` to focus on specific files, or commit more frequently

### No highlighting visible
- **Cause**: No function definition edges changed, or edges don't have `called_function` property
- **Solution**: Check that your code changes include function calls that create dataflow edges

## Future Enhancements

Potential improvements:
- Compare against specific commit (not just HEAD)
- Show diff for regular edges (not just function definitions)
- Highlight nodes connected to changed function edges
- Export diff report as JSON/CSV
- Interactive diff viewer with side-by-side comparison

## Example Workflow

### First Time Setup

1. **Generate initial dataflow analysis:**
   ```bash
   cd dataflow_analysis
   python scalpel_complete_dataflow.py
   ```

2. **Generate initial graph:**
   ```bash
   python generate_interactive_dataflow.py
   ```

3. **Commit the initial graph to git:**
   ```bash
   git add dataflow_graph.html scalpel_complete_dataflow.json
   git commit -m "Add initial dataflow graph"
   ```

### Using Diff Highlighting

1. **Make code changes** that add/modify function calls:
   ```python
   # In extract_and_analyze_image.py
   def test_dataflow_example():
       a = 1
       b = a
       c = 2
       d = b + c
       return d
   ```

2. **Commit your code changes:**
   ```bash
   git add extract_and_analyze_image.py
   git commit -m "Add test dataflow example"
   ```

3. **Regenerate dataflow analysis:**
   ```bash
   cd dataflow_analysis
   python scalpel_complete_dataflow.py
   ```

4. **Regenerate graph with diff highlighting:**
   ```bash
   # Show all changes
   python generate_interactive_dataflow.py
   
   # OR show only changes from specific file
   python generate_interactive_dataflow.py --filter-file extract_and_analyze_image.py
   ```

5. **View the diff:**
   - Open `dataflow_graph.html` in your browser
   - Look for:
     - **Light green edges**: New function definition edges (pulsing)
     - **Orange edges**: Modified function definition edges (pulsing)
     - **Purple edges**: Deleted function definition edges (dashed)
   - Check the legend in bottom-right for change counts

6. **Commit the updated graph:**
   ```bash
   git add dataflow_graph.html scalpel_complete_dataflow.json
   git commit -m "Update dataflow graph with new changes"
   ```

### Viewing Function-Specific Diffs

1. **Open the main graph:**
   ```bash
   # Open dataflow_graph.html in browser
   ```

2. **Click on a function call edge:**
   - Red edges with function calls are clickable
   - Clicking opens the function-specific dataflow page

3. **View function-specific diff:**
   - The function page also shows diff highlighting
   - Only shows changes relevant to that function
   - Same color scheme (light green/orange/purple)

## Notes

- The diff highlighting only works for **function definition edges** (edges with `called_function`)
- Regular dataflow edges (variable-to-variable without function calls) are not highlighted
- The comparison is based on variable names and function names, not line numbers
- Nodes are only highlighted if they're connected to changed function definition edges

