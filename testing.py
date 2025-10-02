from chess_run import *
import chess

def make_new_board(pos: str = None) -> chess.Board:
    board = chess.Board()
    if pos is not None:
        try:
            board.set_fen(pos)
        except ValueError:
            print("Invalid FEN string. Using standard starting position.")
            board.set_fen(chess.STARTING_FEN)    
    else:
        board.set_fen(chess.STARTING_FEN)  
    print_board(board)
    return board


#call run_game_two_bots_greedy_vs_random which is a bot that prioritizes capture moves (greedy) vs a bot that plays random legal moves, 
#greedy bot chosen by color argument
def test_greedy_random_bot():
    board = make_new_board("qq6/k7/8/8/8/8/8/7K b - - 1 1")
    #make two bots play against each other on this particular position
    run_game_two_bots_greedy_vs_random(board, chess.BLACK)
    board = make_new_board(None)
    run_game_two_bots_greedy_vs_random(board, chess.WHITE)
    
#both bots priortize capture
def test_both_greedy_bots():
    board = make_new_board(None)
    #make two bots play against each other on this particular position
    outcome_num = run_game_two_bots_greedy(board)
    assert outcome_num == 3, "Expected a draw due to insufficient material."
if __name__ == "__main__":
    #test_both_greedy_bots()
    test_greedy_random_bot()
 