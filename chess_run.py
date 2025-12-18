# File: /mnt/data/chess_run.py
# -*- coding: utf-8 -*-
import sys
import random
from datetime import datetime
from typing import Optional, Tuple

import chess

# ---------------- UI helpers ----------------
def print_board(board: chess.Board) -> None:
    print("\nCurrent Board Position:")
    print("----------------------")
    print(board)
    print("----------------------\n")


def side_name(color: chess.Color) -> str:
    return "white" if color == chess.WHITE else "black"


def parse_color(s: str) -> Optional[chess.Color]:
    s = s.strip().lower()
    if s in {"w", "white"}:
        return chess.WHITE
    if s in {"b", "black"}:
        return chess.BLACK
    return None


def print_fen(board: chess.Board) -> None:
    print(f"New FEN position: {board.fen()}")


def prompt_user_move(board: chess.Board) -> Optional[chess.Move]:
    side = "White" if board.turn == chess.WHITE else "Black"
    while True:
        s = input(f"{side}: ").strip().lower()
        if s in {"quit", "exit"}:
            print("Goodbye.")
            return None
        if s == "resign":
            loser = side.lower()
            winner = "black" if loser == "white" else "white"
            print(f"{loser.capitalize()} resigns. {winner.capitalize()} wins.")
            return None
        try:
            mv = chess.Move.from_uci(s)
        except ValueError:
            print("Invalid format. Use UCI like e2e4 or a7a8q.")
            continue
        if mv in board.legal_moves:
            return mv
        print("Illegal move in this position. Try again.")


def announce_game_over(board: chess.Board) -> int:
    if board.is_checkmate():
        winner = "white" if board.turn == chess.BLACK else "black"
        print(f"Checkmate. {winner.capitalize()} wins.")
        return 1, winner
    if board.is_stalemate():
        print("Draw by stalemate.")
        return 2, None
    if board.is_insufficient_material():
        print("Draw by insufficient material.")
        return 3, None
    if board.is_seventyfive_moves():
        print("Draw by 75-move rule.")
        return 4, None
    if board.is_fivefold_repetition():
        print("Draw by fivefold repetition.")
        return 5, None
    print("Game over.")
    return 0, None

_rng = random.Random()


def choose_bot_move_capture_pref(board: chess.Board) -> chess.Move:
    legal = list(board.legal_moves)
    if not legal:
        raise RuntimeError("No legal moves available.")
    captures = [m for m in legal if board.is_capture(m)]
    pool = captures if captures else legal
    return _rng.choice(pool)

VAL = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,  
}
# Net gain over a pawn when promoting
PROMOTION_BONUS = {
    chess.QUEEN: 8,   # 9 - 1
    chess.ROOK: 4,    # 5 - 1
    chess.BISHOP: 2,  # 3 - 1
    chess.KNIGHT: 2,  # 3 - 1
}
MATE_SCORE = 1_000


def captured_piece_value(board: chess.Board, move: chess.Move) -> int:
    """Return the captured piece's value (handles en passant)."""
    if board.is_en_passant(move):
        step = -8 if board.turn == chess.WHITE else 8
        sq = move.to_square + step
        return VAL.get(board.piece_type_at(sq) or chess.PAWN, 0)
    pt = board.piece_type_at(move.to_square)
    return VAL.get(pt, 0) if pt else 0


def promotion_value(move: chess.Move) -> int:
    return PROMOTION_BONUS.get(move.promotion, 0) if move.promotion else 0


def immediate_reward(board: chess.Board, move: chess.Move, bot_color: chess.Color) -> int:
    mover = board.turn
    score = 0

    if board.is_capture(move):
        val = captured_piece_value(board, move)
        score += val if mover == bot_color else -val

    promo = promotion_value(move)
    if promo:
        score += promo if mover == bot_color else -promo

    board.push(move)
    try:
        if board.is_checkmate():
            score += MATE_SCORE if mover == bot_color else -MATE_SCORE
    finally:
        board.pop()

    return score


def order_moves(board: chess.Board) -> list[chess.Move]:
    """Lightweight move ordering: checks, captures (MVV), promotions first."""
    moves = list(board.legal_moves)

    def key(m: chess.Move):
        is_cap = board.is_capture(m)
        cap_val = captured_piece_value(board, m) if is_cap else 0
        chk = board.gives_check(m)
        promo = 1 if m.promotion else 0
        return (1 if chk else 0, cap_val, promo)

    moves.sort(key=key, reverse=True)
    return moves

# --- regular min and max algorithm WITHOUT alpha-beta pruning
# Source pseudocode: https://www.chessprogramming.org/Minimax
def min_value(board, depth, bot_color):
    if depth ==0 or board.is_game_over():
        #if game over mate score returned
        if board.is_checkmate():
            return (-MATE_SCORE if board.turn == bot_color else MATE_SCORE), None
        return 0, None
    best_score = 10**9
    best_move = None
    for move in order_moves(board):
        reward = immediate_reward(board, move, bot_color) 
        board.push(move) 
        child_score, _= min_value(board, depth -1, bot_color) 
        board.pop() #remove to avoid future illegal moves 
        #check reward at current depth + one above
        total = reward + child_score
        #update if best_score min found with this possibility
        if total < best_score:
            best_score, best_move = total, move
    return best_score, best_move

def max_value(board, depth, bot_color):
    if depth ==0 or board.is_game_over():
        #if game over mate score returned
        if board.is_checkmate():
            return (-MATE_SCORE if board.turn == bot_color else MATE_SCORE), None
        return 0, None
    best_score = -10**9
    best_move = None 
    for move in order_moves(board):
        reward = immediate_reward(board, move, bot_color) 
        board.push(move) 
        child_score, _ = min_value(board, depth -1, bot_color)  
        board.pop()
        #check reward at current depth + one above
        total = reward + child_score
        #update if best_score exceeded with this possibility
        if total > best_score:
            best_score, best_move = total, move
    return best_score, best_move

def min_max_search(board, depth, bot_color): 
    if board.turn == bot_color:
        #alternate between min and max strategy by bot color
        return max_value(board, depth, bot_color)
    return min_value(board, depth, bot_color)

#same as choose_bot_move except we call minmax instead of search (alpha-beta pruning)
def minmax_choose_bot_move(board, bot_color, depth): 
    if depth <= 0:
        return choose_bot_move_capture_pref(board) 
    _, move = min_max_search(board, depth, bot_color )
    if move is None:
        return choose_bot_move_capture_pref(board) 
    return move
#-----------

def search(board: chess.Board, depth: int, alpha: int, beta: int, bot_color: chess.Color) -> Tuple[int, Optional[chess.Move]]:
    """Alpha-beta minimax that sums rewards along the path for bot_color."""
    #first check game enders
    if depth == 0 or board.is_game_over():
        if board.is_checkmate():
            return (-MATE_SCORE if board.turn == bot_color else MATE_SCORE), None
        return 0, None

    maximizing = (board.turn == bot_color)
    best_move: Optional[chess.Move] = None
    #MAXIMIZING
    #iteratively increasing lower bound (alpha)
    if maximizing:
        #start with min best_score
        best_score = -10**9
        for mv in order_moves(board):
            #compute advantage of move
            imm = immediate_reward(board, mv, bot_color)
            board.push(mv)
            #compute best of future moves, up to depth calls
            child_score, _ = search(board, depth - 1, alpha, beta, bot_color)
            board.pop()
            #undo these moves and get the total advantage score 
            total = imm + child_score
            if total > best_score or (total == best_score and _rng.random() < 0.5):
                best_score, best_move = total, mv
            #update alpha (lower bound) with best_score if exceeded, iteratively increasing alpha as you make moves
            alpha = max(alpha, best_score)
            #beta is upper boud, so can't be less than alpha
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        #MINIMIZING
        #iteratively decreasing upper bound (beta)
        best_score = 10**9
        for mv in order_moves(board):
            imm = immediate_reward(board, mv, bot_color)
            board.push(mv)
            child_score, _ = search(board, depth - 1, alpha, beta, bot_color)
            board.pop()
            total = imm + child_score
            if total < best_score or (total == best_score and _rng.random() < 0.5):
                best_score, best_move = total, mv
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move


#calls alphabeta pruning minmax by default
def choose_bot_move(board: chess.Board, bot_color: chess.Color, depth: int) -> chess.Move:
    """Depth=0 → capture-pref/random; otherwise minimax with alpha-beat."""
    if depth <= 0:
        return choose_bot_move_capture_pref(board)
    _, mv = search(board, depth, -10**9, 10**9, bot_color)
    if mv is None:
        return choose_bot_move_capture_pref(board)
    return mv


def run_game(board: chess.Board, bot_color: chess.Color, depth: int) -> None:
    while True:
        if board.is_game_over():
            announce_game_over(board)
            return

        if board.turn == bot_color:
            mv = choose_bot_move(board, bot_color, depth)
            print(f"Bot (as {side_name(bot_color)}): {mv.uci()}")
            board.push(mv)
            print_fen(board)
            continue

        user_mv = prompt_user_move(board)
        if user_mv is None:
            return
        board.push(user_mv)
        print_fen(board)

#bot prioritizing capture vs bot that just plays randomly
def run_game_two_bots_greedy_vs_random(board: chess.Board, greedy_color: chess.Color) -> None:
    while True:
        if board.is_game_over():
            num_outcome, _ = announce_game_over(board)
            return num_outcome
        #white bot
        if board.turn == chess.WHITE:
            if greedy_color != chess.WHITE:
                legal = list(board.legal_moves)
                if not legal:
                    raise RuntimeError("No legal moves available.")
                mv = random.choice(legal)
                print(f"Bot 1, any legal move (as white): {mv.uci()}")
                board.push(mv)
            else:
                #if it is greedy, it choosees the capture moves specificially
                mv = choose_bot_move(board)
                print(f"Bot 1, prioritizes capture (as white): {mv.uci()}")
                board.push(mv)
        else:
            if greedy_color != chess.BLACK:
                legal = list(board.legal_moves)
                if not legal:
                    raise RuntimeError("No legal moves available.")
                mv = random.choice(legal)
                print(f"Bot 2, any legal move (as black): {mv.uci()}")
                board.push(mv)
            else:
                mv = choose_bot_move(board)
                print(f"Bot 2, prioritizes capture (as black): {mv.uci()}")
                board.push(mv)
        prints(board)
        continue

def prints(board):
    print_fen(board)
    print_board(board)

#both bots do capture move, print not only fen but also current board state for visibility
def run_game_two_bots_greedy(board: chess.Board) -> None:
    while True:
        if board.is_game_over():
            num_outcome, _ = announce_game_over(board)
            return num_outcome
        #white bot
        if board.turn == chess.WHITE:
            mv = choose_bot_move(board)
            print(f"Bot 1 (as white): {mv.uci()}")

"""
This function pits a bot using min max vs a bot using alpha-beta pruning to their min-max strategy
You can set the colors yourself
"""
def run_game_two_bots_minmax_vs_pruning(board,  min_max_color, depth_min_max, depth_alpha_beta): 
    alpha_beta_color = not min_max_color 
    while True:
        if board.is_game_over():
            num_outcome, _ = announce_game_over(board)
            print("For the following configs", min_max_color, depth_min_max, depth_alpha_beta, " outcome is", num_outcome)
            return num_outcome, _
        if board.turn == min_max_color:
            move = minmax_choose_bot_move(board, min_max_color, depth_min_max) 
        else:
            move = choose_bot_move(board, alpha_beta_color, depth_alpha_beta) 
        board.push(move) 
        


# File: /mnt/data/chess_run.py

def play_polish_opening_kings_indian_sokolsky(board: chess.Board) -> None:
    """
      1. b4   Nf6
      2. Bb2  g6
      3. c4   Bg7
      4. e3   d6
      5. Nf3  O-O
      6. d4
    
    """

    uci_sequence = [
        "b2b4",  
        "g8f6",  
        "c1b2",  
        "g7g6",  
        "c2c4",  
        "f8g7",  
        "e2e3",  
        "d7d6",  
        "g1f3",  
        "e8g8",  
        "d2d4",  
    ]

    for u in uci_sequence:
        try:
            mv = chess.Move.from_uci(u)
        except ValueError:
            break
        if mv in board.legal_moves:
            board.push(mv)
        else:
            break

    
def main() -> None:
    print("=====================================================")
    print("             CS 290 Chess Bot Version 0.2            ")
    print("=====================================================")
    print(f"Time: {datetime.now()}")
    print("Computer Player? (w=white/b=black):")
    user_color_in = input().strip().lower()
    bot_color = parse_color(user_color_in)
    if bot_color is None:
        print("Invalid input. Please enter 'w' for white or 'b' for black.")
        sys.exit(1)

    board = chess.Board()
    print("Starting FEN position? (hit ENTER for standard starting postion):")
    pos = input().strip()
    if pos:
        try:
            board.set_fen(pos)
        except ValueError:
            print("Invalid FEN string. Using standard starting position.")
            board.set_fen(chess.STARTING_FEN)
    else:
        board.set_fen(chess.STARTING_FEN)

    # Depth prompt (ENTER defaults to 2)
    try:
        d_in = input("Search depth? (ENTER for 2): ").strip()
        depth = int(d_in) if d_in else 2
    except ValueError:
        print("Bad depth; using 2.")
        depth = 2


    play_polish_opening_kings_indian_sokolsky(board)
    run_game(board, bot_color, depth)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Play again soon.")
