import chess


#iterating moves into board
def game_iter():
    #false for when game outcome 
    return True

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
    print(board.legal_moves)
    print("Starting FEN position? (hit ENTER for standard starting postion):") 
    pos = input().strip()
    if pos:
        try:
            board.set_fen(pos)
        except ValueError:
            print("Invalid FEN string. Using standard starting position.")
    while game_iter(): 
        game_iter() 
    