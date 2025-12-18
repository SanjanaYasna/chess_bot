#!/usr/bin/env python3
"""
Convert a CSV of match results into a LaTeX table, all in one file.

Usage:
  python csv_to_latex_table.py input.csv output.tex

If output file is omitted, defaults to 'results_table.tex'.
If input file is omitted, defaults to 'results.csv'.

The CSV is expected to have the header:
minimax_color,alphabeta_color,depth_minimax,depth_alphabeta,outcome,winner
"""
import csv
import sys
from collections import defaultdict, Counter
import argparse

def escape_latex(s: str) -> str:
    """Minimal LaTeX escaping for characters that may appear in this dataset."""
    if s is None:
        return ""
    s = str(s)
    return s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("$", "\\$") \
            .replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}").replace("~", "\\textasciitilde{}") \
            .replace("^", "\\textasciicircum{}")

def load_groups(csv_path: str):
    """
    Read CSV and group by (minimax_color, alphabeta_color, depth_minimax, depth_alphabeta).
    Returns dict: key -> {"runs": int, "outcome_counts": Counter, "winner_counts": Counter}
    """
    groups = defaultdict(lambda: {"runs": 0, "outcome_counts": Counter(), "winner_counts": Counter()})
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            minimax_color = (row.get("minimax_color") or "").strip()
            alphabeta_color = (row.get("alphabeta_color") or "").strip()
            # try to parse depths as ints for nicer sorting; fall back to raw string
            dm_raw = (row.get("depth_minimax") or "").strip()
            da_raw = (row.get("depth_alphabeta") or "").strip()
            try:
                depth_minimax = int(dm_raw)
            except Exception:
                depth_minimax = dm_raw
            try:
                depth_alphabeta = int(da_raw)
            except Exception:
                depth_alphabeta = da_raw

            outcome = (row.get("outcome") or "").strip() or "(empty)"
            winner = (row.get("winner") or "").strip()  # may be empty

            key = (minimax_color, alphabeta_color, depth_minimax, depth_alphabeta)
            g = groups[key]
            g["runs"] += 1
            g["outcome_counts"][outcome] += 1
            # count only explicit winners from the winner column (expected 'white' or 'black')
            if winner:
                g["winner_counts"][winner] += 1
    return groups

def summarize_group(group):
    """
    Given group with 'runs', 'outcome_counts', 'winner_counts' returns:
      runs, outcome_summary (string), winner_summary (string)
    """
    runs = group["runs"]
    outcome_counts = group["outcome_counts"]
    winner_counts = group["winner_counts"]

    # Build outcome summary: list outcomes by frequency
    oc_list = outcome_counts.most_common()
    outcome_parts = [f"{oc} ({cnt})" for oc, cnt in oc_list]
    outcome_summary = "; ".join(outcome_parts) if outcome_parts else "(none)"

    # Determine winner: based on winner_counts (counts from winner column)
    white_w = winner_counts.get("white", 0)
    black_w = winner_counts.get("black", 0)
    total_checkmate_wins = white_w + black_w
    if total_checkmate_wins == 0:
        winner_summary = "none"
    else:
        if white_w > black_w:
            winner_summary = f"white ({white_w})"
        elif black_w > white_w:
            winner_summary = f"black ({black_w})"
        else:
            winner_summary = f"white ({white_w}) / black ({black_w})"
    return runs, outcome_summary, winner_summary

def sort_key_for_group(item):
    """Sort by depth_minimax, depth_alphabeta, minimax_color, alphabeta_color (depths numeric first)."""
    (minimax_color, alphabeta_color, depth_minimax, depth_alphabeta), _ = item
    def key_for_depth(d):
        if isinstance(d, int):
            return (0, d)  # numeric first
        try:
            # attempt numeric cast
            return (0, int(d))
        except Exception:
            return (1, str(d))  # non-numeric after
    return (key_for_depth(depth_minimax), key_for_depth(depth_alphabeta), str(minimax_color), str(alphabeta_color))

def write_latex_table(groups, output_path: str):
    """Write a LaTeX tabular to output_path summarizing the groups."""
    # Updated header strings as requested:
    header = [
        "Minmax Color",
        "Alphabeta Color",
        "Minmax Depth minimax",
        "Alphabeta Depth",
        "Number Runs",
        "Winner (number per winner)",
        "Outcomes (number per outcome)"
    ]
    sorted_items = sorted(groups.items(), key=sort_key_for_group)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("% Auto-generated LaTeX table\n")
        out.write("\\begin{tabular}{llrrl l p{6cm}}\n")
        out.write("\\hline\n")
        out.write(" & ".join(escape_latex(h) for h in header) + " \\\\\n")
        out.write("\\hline\n")
        for key, group in sorted_items:
            minimax_color, alphabeta_color, depth_minimax, depth_alphabeta = key
            runs, outcome_summary, winner_summary = summarize_group(group)
            cells = [
                escape_latex(minimax_color),
                escape_latex(alphabeta_color),
                escape_latex(depth_minimax),
                escape_latex(depth_alphabeta),
                str(runs),
                escape_latex(winner_summary),
                escape_latex(outcome_summary),
            ]
            out.write(" & ".join(cells) + " \\\\\n")
        out.write("\\hline\n")
        out.write("\\end{tabular}\n")

def main():
    p = argparse.ArgumentParser(description="Convert results CSV to LaTeX table.")
    p.add_argument("input", nargs="?", default="results.csv", help="input CSV path (default: results.csv)")
    p.add_argument("output", nargs="?", default="results_table.tex", help="output .tex path (default: results_table.tex)")
    args = p.parse_args()

    groups = load_groups(args.input)
    if not groups:
        print("No data found in", args.input)
        sys.exit(1)
    write_latex_table(groups, args.output)
    print(f"Wrote LaTeX table to {args.output}")

if __name__ == "__main__":
    main()