# KenKen Display

Generate a printable HTML rendering of a KenKen puzzle from a JSON description.

## Requirements

Python 3.10+ (standard library only — no third-party packages).

## Usage

```sh
# Read puzzle from a file
python3 kenken_display.py -f puzzle.json

# Read puzzle from stdin
cat puzzle.json | python3 kenken_display.py

# Specify a custom output path
python3 kenken_display.py -f puzzle.json -o output.html
```

| Flag | Description |
|------|-------------|
| `-f`, `--file` | Path to a JSON puzzle file. If omitted, reads from stdin. |
| `-o`, `--output` | Output HTML file path. Defaults to the input filename with an `.html` extension, or `kenken.html` when reading from stdin. |

The generated HTML file is written to disk and automatically opened in your default browser. Use **Ctrl/Cmd + P** to print.

For any cage with 3 or more cells (using `+` or `×`), the program calculates all possible number combinations that satisfy the target and displays them below the grid.

## JSON Format

```json
{
  "grid_size": 4,
  "cages": [
    { "target": 2,  "operation": "÷", "cells": [[0, 0], [1, 0]] },
    { "target": 3,  "operation": "-", "cells": [[0, 1], [0, 2]] },
    { "target": 1,  "operation": null, "cells": [[0, 3]] }
  ]
}
```

| Field | Description |
|-------|-------------|
| `grid_size` | Integer N for the N×N grid. |
| `cages` | Array of cage objects. |
| `cages[].target` | Target number for the cage (integer). |
| `cages[].operation` | One of `"+"`, `"-"`, `"×"`, `"÷"`, or `null` for single-cell cages. |
| `cages[].cells` | Array of `[row, col]` positions (0-indexed, top-left origin). |

A sample puzzle is included in `sample_4x4.json` and `sample_6x6.json` (which demonstrates the combination hints).
