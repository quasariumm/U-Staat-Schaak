import logic
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
        if depth == 0 or logic.mate:
            return None, Calculations.evaluation(max_color)
        moves = Calculations.all_legal_moves()
        best_move = random.choice(list(moves.values()))
        if max_player:
            max_eval = -math.inf
            for pieceType, move in moves.items():
                row, file = logic.Utils.index_to_rowfile(int(move[2:4]))
                mrow, mfile = logic.Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(logic.piecesLayout)
                logic.piecesLayout[row][file] = None
                logic.piecesLayout[mrow][mfile] = pieceType
                current_eval = Calculations.minimax(depth-1, alpha, beta, False, max_color)
                logic.piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval[1] > max_eval:
                    max_eval = current_eval[1]
                    best_move = move
                alpha = max(alpha, current_eval[1])
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            max_eval = math.inf
            for pieceType, move in moves.items():
                row, file = logic.Utils.index_to_rowfile(int(move[2:4]))
                mrow, mfile = logic.Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(logic.piecesLayout)
                logic.piecesLayout[row][file] = None
                logic.piecesLayout[mrow][mfile] = pieceType
                current_eval = Calculations.minimax(depth-1, alpha, beta, True, max_color)
                logic.piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval[1] < max_eval:
                    max_eval = current_eval[1]
                    best_move = move
                beta = min(beta, current_eval[1])
                if beta <= alpha:
                    break
            return best_move, max_eval

    def all_legal_moves():
        white_pieces, black_pieces = logic.Backend.black_and_white_pieces_list()
        moves = {}
        for el in (white_pieces if logic.white_to_move else black_pieces):
            row, file = logic.Utils.button_to_rowfile(el)
            pieceType = logic.piecesLayout[row][file]
            moves.update({pieceType: move for move in logic.Backend.legal_moves(el)})
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