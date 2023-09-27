from logic import piecesLayout, white_to_move, mate, Backend, Utils
from pieces import White as w
from pieces import Black as b

from copy import deepcopy
import math, random

WHITE = 0
BLACK = 1

weights = {
    w.King: 900,
    w.Queen: 90,
    w.Rook: 50,
    w.Knight: 30,
    w.Bishop: 30,
    w.Pawn: 10,
    b.King: 900,
    b.Queen: 90,
    b.Rook: 50,
    b.Knight: 30,
    b.Bishop: 30,
    b.Pawn: 10
}
white_score = 0
black_score = 0

class Calculations():
    def minimax(depth:int, alpha:float, beta:float, max_player:bool, max_color:int):
        if depth == 0 or mate:
            return None, Calculations.evaluation(max_color)
        moves = Calculations.all_legal_moves()
        best_move = random.choice(moves)
        if max_player:
            max_eval = -math.inf
            for pieceType, move in moves.items():
                row, file = Utils.index_to_rowfile(int(move[2:4]))
                mrow, mfile = Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(piecesLayout)
                piecesLayout[row][file] = None
                piecesLayout[mrow][mfile] = pieceType
                current_eval = Calculations.minimax(depth-1, alpha, beta, False, max_color)
                piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            max_eval = math.inf
            for pieceType, move in moves.items():
                row, file = Utils.index_to_rowfile(int(move[2:4]))
                mrow, mfile = Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(piecesLayout)
                piecesLayout[row][file] = None
                piecesLayout[mrow][mfile] = pieceType
                current_eval = Calculations.minimax(depth-1, alpha, beta, True, max_color)
                piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval < max_eval:
                    max_eval = current_eval
                    best_move = move
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            print(piecesLayout)
            return best_move, max_eval

    def all_legal_moves():
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        moves = {}
        for el in (white_pieces if white_to_move else black_pieces):
            row, file = Utils.button_to_rowfile(el)
            pieceType = piecesLayout[row][file]
            moves += {pieceType: move for move in Backend.legal_moves(el)}
        return moves

    def calculate_score(layout):
        global white_score, black_score
        white_score, black_score = 0
        for el in layout:
            if issubclass(type(el), (w.King, w.Queen, w.Rook, w.Knight, w.Bishop, w.Pawn)):
                white_score += weights[type(el)]
            elif el != None:
                black_score += weights[type(el)]
    
    def evaluation(color):
        global white_score, black_score
        if color == WHITE:
            return white_score - black_score
        else:
            return black_score - white_score