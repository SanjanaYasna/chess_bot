
import sys
import argparse
import importlib.util
from dataclasses import dataclass
from typing import List, Dict, Any

import chess
import pandas as pd

MODULE_PATH = "chess_run.py"  # or "./src/chess_run.py"
spec = importlib.util.spec_from_file_location("chess_run", MODULE_PATH)
if spec is None or spec.loader is None:
    print(f"Cannot load module from {MODULE_PATH}", file=sys.stderr)
    sys.exit(1)
chess_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chess_run)  # type: ignore

VAL = chess_run.VAL  # use the bot's small-scale values

def material_eval(board: chess.Board) -> int:
    """Material from White's perspective using VAL."""
    score = 0
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p is None:
            continue
        v = VAL.get(p.piece_type, 0)
        score += v if p.color == chess.WHITE else -v
    return score

@dataclass
class OpeningCase:
    name: str
    uci_first_move: str

OPENINGS: List[OpeningCase] = [
    OpeningCase("King's Pawn", "e2e4"),
    OpeningCase("Queen's Pawn", "d2d4"),
    OpeningCase("English", "c2c4"),
    OpeningCase("Reti", "g1f3"),
    OpeningCase("Bird", "f2f4"),
    OpeningCase("Nimzo-Larsen", "b2b3"),
    OpeningCase("King's Fianchetto", "g2g3"),
    OpeningCase("Van Geet", "b1c3"),
    OpeningCase("Saragossa", "c2c3"),
    OpeningCase("Polish/Orangutan", "b2b4"),
    OpeningCase("Grob", "g2g4"),
    OpeningCase("Kadas", "h2h4"),
]

def play_one(opening: OpeningCase, depth: int, max_plies: int) -> Dict[str, Any]:
    board = chess.Board()
    # Force White's first move
    try:
        m = chess.Move.from_uci(opening.uci_first_move)
    except ValueError:
        return {
            "Opening": opening.name,
            "White first move (UCI)": opening.uci_first_move,
            "Plies": 0,
            "Result": "*",
            "Material (W-B)": 0,
            "Terminal reason": "Invalid opening UCI",
        }
    if m not in board.legal_moves:
        return {
            "Opening": opening.name,
            "White first move (UCI)": opening.uci_first_move,
            "Plies": 0,
            "Result": "*",
            "Material (W-B)": 0,
            "Terminal reason": "Illegal opening in start position",
        }
    board.push(m)
    plies = 1

    # Self-play: both sides use your bot
    while not board.is_game_over() and plies < max_plies:
        side_to_move = board.turn  # True: white, False: black
        mv = chess_run.choose_bot_move(board, side_to_move, depth)
        board.push(mv)
        plies += 1

    # Determine terminal reason
    if board.is_checkmate():
        terminal = "checkmate"
    elif board.is_stalemate():
        terminal = "stalemate"
    elif board.is_insufficient_material():
        terminal = "insufficient material"
    elif board.is_seventyfive_moves():
        terminal = "75-move rule"
    elif board.is_fivefold_repetition():
        terminal = "fivefold repetition"
    else:
        terminal = "max plies or other"

    return {
        "Opening": opening.name,
        "White first move (UCI)": opening.uci_first_move,
        "Plies": plies,
        "Result": board.result(claim_draw=True),  # "1-0", "0-1", "1/2-1/2" or "*"
        "Material (W-B)": material_eval(board),
        "Terminal reason": terminal,
    }

def main():
    ap = argparse.ArgumentParser(description="Self-play opening tests for chess_run minimax bot")
    ap.add_argument("--depth", type=int, default=2, help="Search depth for both sides (default: 2)")
    ap.add_argument("--plies", type=int, default=120, help="Max plies to play per game (default: 120)")
    ap.add_argument("--csv", type=str, default="", help="Optional path to save CSV results")
    args = ap.parse_args()

    rows: List[Dict[str, Any]] = []
    for op in OPENINGS:
        rows.append(play_one(op, depth=args.depth, max_plies=args.plies))

    df = pd.DataFrame(rows).sort_values(
        by=["Result", "Material (W-B)"], ascending=[False, False]
    ).reset_index(drop=True)

    print("\n=== Opening self-play results ===")
    print(df.to_string(index=False))

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"\nSaved results to {args.csv}")

    print("\nAggregate by Result:")
    print(df.groupby("Result").size().to_frame("Count"))

if __name__ == "__main__":
    main()
