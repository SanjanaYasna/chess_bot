import chess


#iterating moves into board
def game_iter():
    #false for when game outcome 
    return True

def print_board(board):
    print("\nCurrent Board Position:")
    print("----------------------")
    print(board)
    print("----------------------\n")
    
if __name__ == "__main__":
    #have user 
    print("Computer Player? (w=white/b=black):")
    #get user input
    user_color = input().strip().lower()
    if user_color not in ['w', 'b']:
        print("Invalid input. Please enter 'w' for white or 'b' for black.")
        exit(1)
    #init board 
    board = chess.Board()
    print("Starting FEN position? (hit ENTER for standard starting postion):") 
    pos = input().strip()
    #check if pos was just enter
    pos = pos if pos else None
    if pos is not None:
        try:
            board.set_fen(pos)
            print_board(board)
        except ValueError:
            print("Invalid FEN string. Using standard starting position.")
            #set default fen for side
            board.set_fen(chess.STARTING_FEN)    
            print_board(board)
    else:
        board.set_fen(chess.STARTING_FEN)  
        print_board(board)
    
    #while moves sitll valid, we alternate between black and white 
    while not board.is_check() and not board.is_stalemate(): 
        game_iter() 
    