#!/usr/bin/env python3
"""Display a KenKen grid suitable for printing by generating an HTML file."""

import argparse
import json
import sys
import webbrowser
from itertools import combinations_with_replacement, permutations
from math import prod
from pathlib import Path
from typing import Optional


def load_puzzle(file) -> dict:
    return json.load(file)


def build_cage_map(cages: list, grid_size: int) -> list[list[int]]:
    """Map each cell to its cage index."""
    cage_map = [[-1] * grid_size for _ in range(grid_size)]
    for idx, cage in enumerate(cages):
        for r, c in cage["cells"]:
            cage_map[r][c] = idx
    return cage_map


def find_label_cell(cage: dict) -> tuple[int, int]:
    """Return the top-left-most cell of a cage (for placing the label)."""
    cells = cage["cells"]
    return min(cells, key=lambda rc: (rc[0], rc[1]))


def find_combinations(target: int, operation: str, num_cells: int, grid_size: int) -> list[tuple[int, ...]]:
    """Return sorted tuples of numbers (1..grid_size) that satisfy the cage constraint."""
    results = []
    for combo in combinations_with_replacement(range(1, grid_size + 1), num_cells):
        if operation == "+" and sum(combo) == target:
            results.append(combo)
        elif operation == "×" and prod(combo) == target:
            results.append(combo)
    return results


def check_cage(cage: dict, grid: list[list[int]]) -> bool:
    """Return True if the cage constraint is satisfied by current grid values."""
    values = [grid[r][c] for r, c in cage["cells"]]
    target = cage["target"]
    op = cage.get("operation")
    if op is None:
        return values[0] == target
    if op == "+":
        return sum(values) == target
    if op == "×":
        return prod(values) == target
    if op == "-":
        return abs(values[0] - values[1]) == target
    if op == "÷":
        a, b = values
        return (a % b == 0 and a // b == target) or (b % a == 0 and b // a == target)
    return False


def solve(puzzle: dict) -> Optional[list]:
    """Solve a KenKen puzzle using backtracking. Returns grid or None."""
    n = puzzle["grid_size"]
    cages = puzzle["cages"]
    grid = [[0] * n for _ in range(n)]

    # Map each cell to its cage
    cell_to_cage: dict[tuple[int, int], dict] = {}
    for cage in cages:
        for r, c in cage["cells"]:
            cell_to_cage[(r, c)] = cage

    # Order cells left-to-right, top-to-bottom
    cells = [(r, c) for r in range(n) for c in range(n)]

    def is_valid(r: int, c: int, val: int) -> bool:
        # Check row and column uniqueness
        for i in range(n):
            if grid[r][i] == val:
                return False
            if grid[i][c] == val:
                return False
        return True

    def cage_feasible(r: int, c: int) -> bool:
        cage = cell_to_cage[(r, c)]
        cage_cells = cage["cells"]
        values = [grid[cr][cc] for cr, cc in cage_cells]
        if 0 in values:
            # Cage incomplete — do a partial check
            filled = [v for v in values if v != 0]
            target = cage["target"]
            op = cage.get("operation")
            if op == "+":
                return sum(filled) < target or (0 not in values and sum(filled) == target)
            if op == "×":
                p = prod(filled) if filled else 1
                return p <= target or (0 not in values and p == target)
            return True
        return check_cage(cage, grid)

    def backtrack(idx: int) -> bool:
        if idx == len(cells):
            return True
        r, c = cells[idx]
        for val in range(1, n + 1):
            if is_valid(r, c, val):
                grid[r][c] = val
                if cage_feasible(r, c) and backtrack(idx + 1):
                    return True
                grid[r][c] = 0
        return False

    if backtrack(0):
        return grid
    return None


def generate_html(puzzle: dict, solution: Optional[list] = None) -> str:
    grid_size = puzzle["grid_size"]
    cages = puzzle["cages"]
    cage_map = build_cage_map(cages, grid_size)

    # Build label lookup: (row, col) -> label string
    labels: dict[tuple[int, int], str] = {}
    for cage in cages:
        r, c = find_label_cell(cage)
        op = cage.get("operation") or ""
        labels[(r, c)] = f"{cage['target']}{op}"

    # Build border info per cell
    THIN = "1px solid #ccc"
    THICK = "3px solid #000"

    cell_styles: list[list[dict]] = []
    for r in range(grid_size):
        row_styles = []
        for c in range(grid_size):
            style: dict[str, str] = {}
            # Top border
            if r == 0:
                style["border-top"] = THICK
            elif cage_map[r][c] != cage_map[r - 1][c]:
                style["border-top"] = THICK
            else:
                style["border-top"] = THIN

            # Left border
            if c == 0:
                style["border-left"] = THICK
            elif cage_map[r][c] != cage_map[r][c - 1]:
                style["border-left"] = THICK
            else:
                style["border-left"] = THIN

            # Bottom border
            if r == grid_size - 1:
                style["border-bottom"] = THICK
            elif cage_map[r][c] != cage_map[r + 1][c]:
                style["border-bottom"] = THICK
            else:
                style["border-bottom"] = THIN

            # Right border
            if c == grid_size - 1:
                style["border-right"] = THICK
            elif cage_map[r][c] != cage_map[r][c + 1]:
                style["border-right"] = THICK
            else:
                style["border-right"] = THIN

            row_styles.append(style)
        cell_styles.append(row_styles)

    # Cell size scales with grid
    cell_size = max(40, 360 // grid_size)
    font_size = max(10, cell_size // 4)
    solution_font = max(16, cell_size // 2)

    # Build HTML
    rows_html = []
    for r in range(grid_size):
        cells_html = []
        for c in range(grid_size):
            s = cell_styles[r][c]
            inline = "; ".join(f"{k}: {v}" for k, v in s.items())
            label = labels.get((r, c), "")
            # if label ends with %, change that character
            if label.endswith("÷"):
                label = label[:-1] + "%"
            label_span = (
                f'<span class="label">{label}</span>' if label else ""
            )
            sol_span = ""
            if solution:
                sol_span = f'<span class="solution">{solution[r][c]}</span>'
            cells_html.append(
                f'<td style="{inline}">{label_span}{sol_span}</td>'
            )
        rows_html.append("<tr>" + "".join(cells_html) + "</tr>")

    table_html = "\n      ".join(rows_html)

    # Build hints for cages with 3+ cells
    hints_html = ""
    large_cages = [
        cage for cage in cages
        if len(cage["cells"]) >= 3 and cage.get("operation") in ("+", "×")
    ]
    if large_cages:
        hint_items = []
        for cage in large_cages:
            op = cage["operation"]
            label = f"{cage['target']}{op}"
            combos = find_combinations(cage["target"], op, len(cage["cells"]), grid_size)
            combo_strs = [", ".join(str(n) for n in c) for c in combos]
            formatted = "; &nbsp;".join(f"{{{s}}}" for s in combo_strs)
            hint_items.append(
                f"<li><strong>{label}</strong> ({len(cage['cells'])} cells): {formatted}</li>"
            )
        hints_html = (
            '<div class="hints"><h3>Possible combinations</h3><ul>'
            + "\n".join(hint_items)
            + "</ul></div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>KenKen {grid_size}×{grid_size}</title>
<style>
  @media print {{
    body {{ margin: 0; }}
  }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
  }}
  table {{
    border-collapse: collapse;
  }}
  td {{
    width: {cell_size}px;
    height: {cell_size}px;
    position: relative;
    vertical-align: top;
    padding: 0;
  }}
  .label {{
    position: absolute;
    top: 2px;
    left: 3px;
    font-size: {font_size}px;
    font-weight: bold;
    line-height: 1;
  }}
  .solution {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: {solution_font}px;
    color: #333;
  }}
  .hints {{
    margin-top: 24px;
    font-size: 14px;
  }}
  .hints h3 {{
    margin: 0 0 8px;
    font-size: 16px;
  }}
  .hints ul {{
    margin: 0;
    padding-left: 20px;
  }}
  .hints li {{
    margin-bottom: 4px;
  }}
</style>
</head>
<body>
  <table>
      {table_html}
  </table>
  {hints_html}
</body>
</html>
"""

def puzzle_filename(puzzle: dict) -> str:
    """Build a filename from cage labels, replacing operation symbols."""
    labels = []
    for cage in puzzle["cages"]:
        op = cage.get("operation") or ""
        labels.append(f"{cage['target']}{op}")
    name = ",".join(labels)
    name = name.replace("+", "p").replace("-", "m").replace("×", "x").replace("÷", "d")
    return name


def main():
    parser = argparse.ArgumentParser(description="Display a KenKen grid as printable HTML.")
    parser.add_argument("-f", "--file", type=argparse.FileType("r"),
                        help="JSON puzzle file (default: read from stdin)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output HTML file path")
    parser.add_argument("--solve", action="store_true",
                        help="Solve the puzzle and print answers in the grid")
    args = parser.parse_args()

    if args.file:
        puzzle = load_puzzle(args.file)
        default_out = Path(args.file.name).with_suffix(".html")
    else:
        puzzle = load_puzzle(sys.stdin)
        base = puzzle_filename(puzzle)
        Path(f"{base}.json").write_text(json.dumps(puzzle, indent=2, ensure_ascii=False))
        default_out = Path(f"{base}.html")

    solution = None
    if args.solve:
        solution = solve(puzzle)
        if solution is None:
            print("No solution found.", file=sys.stderr)
            sys.exit(1)

    html = generate_html(puzzle, solution)
    out_path = Path(args.output) if args.output else default_out
    out_path.write_text(html)
    print(f"Written to {out_path}")
    webbrowser.open(out_path.resolve().as_uri())


if __name__ == "__main__":
    main()
