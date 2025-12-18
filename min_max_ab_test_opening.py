import csv
import multiprocessing as mp
from chess_run import *
from testing_openings import *


# File: /mnt/data/chess_run.py

# Opening positions after the specified lines are played (from standard start).
OPENING_FENS = {
    "Queen's Gambit": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2",
    "Sicilian Defense (Dragon Variation)": "rnbqkb1r/pp2pp1p/3p1np1/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6",
    "Polish Opening: King's Indian Variation, Sokolsky Attack": "rnbq1rk1/ppp1ppbp/3p1np1/8/1PPP4/4PN2/PB3PPP/RN1QKB1R b KQ - 0 6",
}

def choose_opening_and_make_board(choice: int | None = None) -> "chess.Board":
    """
    Argument-driven, brute-force:
    - 1 -> Queen's Gambit
    - 2 -> Sicilian Defense (Dragon)
    - 3 -> Polish Opening: King's Indian Variation, Sokolsky Attack
    - Else -> standard start
    Returns only the board; no prints.
    """
    board = chess.Board()
    board.set_fen(chess.STARTING_FEN)

    names = list(OPENING_FENS.keys())
    if isinstance(choice, int) and 1 <= choice <= len(names):
        fen = OPENING_FENS[names[choice - 1]]
        try:
            board.set_fen(fen)
        except ValueError:
            board.set_fen(chess.STARTING_FEN)

    return board


OUTCOME_LABELS = {
    0: "game_over",
    1: "checkmate",
    2: "stalemate",
    3: "insufficient_material",
    4: "seventyfive_move_rule",
    5: "fivefold_repetition",
}

def _run_single_match(job_args):
    minimax_color, depth_minimax, depth_alphabeta = job_args
    board = choose_opening_and_make_board(1)
    outcome = run_game_two_bots_minmax_vs_pruning(
        board,
        minimax_color,
        depth_minimax,
        depth_alphabeta,
    )
    outcome_label = OUTCOME_LABELS.get(outcome, "unknown")
    return (
        side_name(minimax_color),
        depth_minimax,
        depth_alphabeta,
        outcome_label,
    )


def run_all_minimax_vs_pruning_experiments(
    output_path: str = "minimax_vs_alphabeta_results_opening.csv",
) -> None:
    jobs = []

    #add jobs per config
    def add_jobs(color: chess.Color, depth_minimax: int, depth_alphabeta: int, count: int):
        for _ in range(count):
            jobs.append((color, depth_minimax, depth_alphabeta))

    #30 jobs total
    add_jobs(chess.WHITE, 3, 3, 3)
    add_jobs(chess.BLACK, 3, 3, 3)
    add_jobs(chess.WHITE, 2, 4, 3)
    add_jobs(chess.BLACK, 2, 4, 3)
    add_jobs(chess.WHITE, 4, 2, 3)
    add_jobs(chess.BLACK, 4, 2, 3)
    #run on at a time
    with mp.Pool() as pool:
        results = pool.map(_run_single_match, jobs)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["minimax_color", "alphabeta_color", "depth_minimax", "depth_alphabeta", "outcome"]
        )
        for color, depth_minimax, depth_alphabeta, outcome_label in results:
            alphabeta_color = "white" if color == "black" else "black"
            writer.writerow([color, alphabeta_color, depth_minimax, depth_alphabeta, outcome_label])
    
if __name__ == "__main__":
    run_all_minimax_vs_pruning_experiments()