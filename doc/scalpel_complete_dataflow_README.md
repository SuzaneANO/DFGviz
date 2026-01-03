# Scalpel Complete Dataflow Analysis - JSON Structure

## Overview

The `scalpel_complete_dataflow.json` file contains **complete variable-to-variable dataflow** analysis from all Python files in your codebase.

## Statistics

- **Total variables**: 1,494 unique variables
- **Total definitions**: 2,752 variable definitions
- **Total uses**: 11,939 variable uses
- **Total dataflow edges**: 200 variable-to-variable flows

## JSON Structure

```json
{
  "metadata": {
    "total_variables": 1494,
    "total_definitions": 2752,
    "total_uses": 11939,
    "total_dataflow_edges": 200
  },
  "variables": {
    "variable_name": {
      "definitions": {
        "count": <number>,
        "locations": [
          {
            "line": <line_number>,
            "function": "<function_name>",
            "file": "<file_path>",
            "type": "assignment" | "parameter",
            "value_source": "<source_variable>" | null
          }
        ]
      },
      "uses": {
        "count": <number>,
        "locations": [
          {
            "line": <line_number>,
            "function": "<function_name>",
            "file": "<file_path>",
            "context": "variable_read" | "function_argument" | "return_value" | ...
          }
        ]
      },
      "dataflow_outgoing": {
        "count": <number>,
        "flows": [
          {
            "target_variable": "<target_var_name>",
            "source_line": <line_number>,
            "target_line": <line_number>,
            "function": "<function_name>",
            "file": "<file_path>",
            "flow_type": "assignment" | "augmented_assignment"
          }
        ],
        "target_variables": ["<var1>", "<var2>", ...]
      },
      "dataflow_incoming": {
        "count": <number>,
        "flows": [
          {
            "source_variable": "<source_var_name>",
            "source_line": <line_number>,
            "target_line": <line_number>,
            "function": "<function_name>",
            "file": "<file_path>",
            "flow_type": "assignment" | "augmented_assignment"
          }
        ],
        "source_variables": ["<var1>", "<var2>", ...]
      }
    }
  }
}
```

## Understanding Each Section

### 1. Definitions

Shows **where each variable is created/defined**:
- **`count`**: Number of times this variable is defined
- **`locations`**: List of all definition locations with:
  - `line`: Line number where defined
  - `function`: Function where defined
  - `file`: File path
  - `type`: "assignment" or "parameter"
  - `value_source`: What variable/value it comes from (if from another variable)

**Example**:
```json
"definitions": {
  "count": 3,
  "locations": [
    {
      "line": 135,
      "function": "convert_constraints_to_lp",
      "file": ".\\core\\constraint_converter.py",
      "type": "assignment",
      "value_source": "array()"
    }
  ]
}
```

### 2. Uses

Shows **where each variable is read/used**:
- **`count`**: Number of times this variable is used
- **`locations`**: List of all usage locations with:
  - `line`: Line number where used
  - `function`: Function where used
  - `file`: File path
  - `context`: How it's used (e.g., "variable_read", "function_argument", "return_value")

**Example**:
```json
"uses": {
  "count": 10,
  "locations": [
    {
      "line": 148,
      "function": "convert_constraints_to_lp",
      "file": ".\\core\\constraint_converter.py",
      "context": "variable_read"
    }
  ]
}
```

### 3. Dataflow Outgoing

Shows **what variables this variable flows TO**:
- **`count`**: Number of variables this flows to
- **`flows`**: Detailed flow information:
  - `target_variable`: Variable that receives this value
  - `source_line`: Line where source variable is used
  - `target_line`: Line where target variable is assigned
  - `function`: Function where flow occurs
  - `file`: File path
  - `flow_type`: Type of flow ("assignment", "augmented_assignment")
- **`target_variables`**: List of all variables this flows to

**Example**:
```json
"dataflow_outgoing": {
  "count": 2,
  "flows": [
    {
      "target_variable": "result",
      "source_line": 100,
      "target_line": 101,
      "function": "my_function",
      "file": ".\\core\\utils.py",
      "flow_type": "assignment"
    }
  ],
  "target_variables": ["result", "output"]
}
```

### 4. Dataflow Incoming

Shows **what variables flow INTO this variable**:
- **`count`**: Number of variables that flow into this
- **`flows`**: Detailed flow information (same structure as outgoing)
- **`source_variables`**: List of all variables that flow into this

**Example**:
```json
"dataflow_incoming": {
  "count": 1,
  "flows": [
    {
      "source_variable": "input_data",
      "source_line": 50,
      "target_line": 51,
      "function": "process_data",
      "file": ".\\core\\utils.py",
      "flow_type": "assignment"
    }
  ],
  "source_variables": ["input_data"]
}
```

## Example: Complete Variable Flow

For a variable like `widths`:

```json
"widths": {
  "definitions": {
    "count": 5,
    "locations": [
      {"line": 100, "function": "main", "file": "...", "type": "assignment"},
      ...
    ]
  },
  "uses": {
    "count": 19,
    "locations": [
      {"line": 200, "function": "loss_function", "context": "function_argument"},
      ...
    ]
  },
  "dataflow_outgoing": {
    "count": 3,
    "flows": [
      {
        "target_variable": "normalized_widths",
        "source_line": 100,
        "target_line": 101,
        "function": "normalize",
        "flow_type": "assignment"
      }
    ],
    "target_variables": ["normalized_widths", "widths_array", "result"]
  },
  "dataflow_incoming": {
    "count": 2,
    "flows": [
      {
        "source_variable": "input_widths",
        "source_line": 50,
        "target_line": 100,
        "function": "main",
        "flow_type": "assignment"
      }
    ],
    "source_variables": ["input_widths", "config_widths"]
  }
}
```

This shows:
- `widths` is defined 5 times
- `widths` is used 19 times
- `widths` flows TO 3 other variables (normalized_widths, widths_array, result)
- `widths` receives values FROM 2 variables (input_widths, config_widths)

## How to Use This Data

### Find All Variables That Flow Into a Variable:
```python
import json
data = json.load(open('scalpel_complete_dataflow.json'))
var = 'widths'
sources = data['variables'][var]['dataflow_incoming']['source_variables']
print(f"Variables that flow into {var}: {sources}")
```

### Find All Variables That a Variable Flows To:
```python
targets = data['variables'][var]['dataflow_outgoing']['target_variables']
print(f"Variables that {var} flows to: {targets}")
```

### Find Complete Dataflow Chain:
```python
def trace_dataflow(var, visited=None):
    if visited is None:
        visited = set()
    if var in visited:
        return []
    visited.add(var)
    
    chain = [var]
    sources = data['variables'][var]['dataflow_incoming']['source_variables']
    if sources:
        for source in sources:
            chain = trace_dataflow(source, visited) + chain
    return chain

chain = trace_dataflow('widths')
print(f"Complete flow chain: {' → '.join(chain)}")
```

### Find All Uses of a Variable:
```python
uses = data['variables'][var]['uses']['locations']
for use in uses:
    print(f"Used at line {use['line']} in {use['function']} ({use['file']})")
```

## Key Features

1. **Complete Coverage**: Every variable in every file
2. **Bidirectional Flow**: Both incoming and outgoing flows
3. **Line-Level Precision**: Exact line numbers for all definitions and uses
4. **Function Context**: Which function each definition/use occurs in
5. **File Tracking**: Which file each variable is in
6. **Flow Types**: Distinguishes between assignment and augmented assignment

## Generated By

- **Script**: `scalpel_complete_dataflow.py`
- **Method**: AST-based analysis using Python's `ast` module
- **Output**: Single JSON file with complete dataflow information

