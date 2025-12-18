from chess_run import *
import chess

# File: /mnt/data/chess_run.py

# Opening positions after the specified lines are played (from standard start).
OPENING_FENS = {
    "Queen's Gambit": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2",
    "Sicilian Defense (Dragon Variation)": "rnbqkb1r/pp2pp1p/3p1np1/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6",
    "Polish Opening: King's Indian Variation, Sokolsky Attack": "rnbq1rk1/ppp1ppbp/3p1np1/8/1PPP4/4PN2/PB3PPP/RN1QKB1R b KQ - 0 6",
}

def choose_opening_and_make_board(choice: int | None = None) -> "chess.Board":
    """
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



def test_greedy_random_bot():
    board = choose_opening_and_make_board(1)
    #make two bots play against each other on this particular position
    run_game_two_bots_greedy_vs_random(board, chess.BLACK)

    board = choose_opening_and_make_board(1)
    #make two bots play against each other on this particular position
    run_game_two_bots_greedy_vs_random(board, chess.WHITE)
    
    board = choose_opening_and_make_board(2)
    run_game_two_bots_greedy_vs_random(board, chess.WHITE)

    board = choose_opening_and_make_board(2)
    run_game_two_bots_greedy_vs_random(board, chess.BLACK)

    
#both bots priortize capture
def test_both_greedy_bots():
    board = choose_opening_and_make_board(1)
    #make two bots play against each other on this particular position
    outcome_num = run_game_two_bots_greedy(board)
    assert outcome_num == 3, "Expected a draw due to insufficient material."


if __name__ == "__main__":
    #test_both_greedy_bots()
    test_greedy_random_bot()