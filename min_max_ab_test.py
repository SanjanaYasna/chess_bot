import csv
import multiprocessing as mp
from chess_run import *

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
    board = chess.Board()
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
    output_path: str = "minimax_vs_alphabeta_results.csv",
) -> None:
    jobs = []

    #add jobs per config
    def add_jobs(color: chess.Color, depth_minimax: int, depth_alphabeta: int, count: int):
        for _ in range(count):
            jobs.append((color, depth_minimax, depth_alphabeta))

    #30 jobs total
    add_jobs(chess.WHITE, 3, 3, 10)
    add_jobs(chess.BLACK, 3, 3, 10)
    add_jobs(chess.WHITE, 2, 4, 10)
    add_jobs(chess.BLACK, 2, 4, 10)
    add_jobs(chess.WHITE, 4, 2, 10)
    add_jobs(chess.BLACK, 4, 2, 10)
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