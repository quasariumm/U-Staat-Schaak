import logic
from pieces import White as w
from pieces import Black as b

from copy import deepcopy
import math, random

WHITE = 1
BLACK = -1

weights = {
    w.Queen: 900,
    w.Rook: 500,
    w.Knight: 300,
    w.Bishop: 320,
    w.Pawn: 100,
    b.Queen: 900,
    b.Rook: 500,
    b.Knight: 300,
    b.Bishop: 320,
    b.Pawn: 100
}

ENDGAME_MATERIAL_START = 2 * weights[w.Rook] + weights[w.Bishop] + weights[w.Knight]
MATERIAL_START = 2 * weights[w.Rook] + 2 * weights[w.Bishop] + 2 * weights[w.Knight] + weights[w.Queen]

# https://www.chessprogramming.org/Simplified_Evaluation_Function
pawn_square_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5,  10, 25, 25, 10,  5,  5,
    0,  0,  0,  20, 20,  0,  0,  0,
    5, -5, -10,  0,  0,-10, -5,  5,
    5, 10, 10, -20,-20, 10, 10,  5,
    0,  0,  0,   0,  0,  0,  0,  0
]
knight_square_table = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]
bishop_square_table = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]
rook_square_table = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]
queen_square_table = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]
king_square_table = [
    [ # Middlegame
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20
    ],
    [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]
]

piece_square_tables = {
    w.Pawn: pawn_square_table,
    b.Pawn: pawn_square_table,
    w.Knight: knight_square_table,
    b.Knight: knight_square_table,
    w.Bishop: bishop_square_table,
    b.Bishop: bishop_square_table,
    w.Rook: rook_square_table,
    b.Rook: rook_square_table,
    w.Queen: queen_square_table,
    b.Queen: queen_square_table,
    w.King: king_square_table,
    b.King: king_square_table
}

class Calculations():
    # TODO: makes pawns out of nowhere
    def minimax(depth:int, alpha:float, beta:float, max_player:bool, max_color:int, check:bool):
        if depth == 0 or logic.mate:
            return None, Calculations.evaluation(max_color)
        moves = Misc.all_legal_moves(max_player)
        if len(moves) == 0:
            if check:
                return depth, math.inf * (WHITE if max_player else BLACK)
            return 'stalemate', 0 # Stalemate
        best_move = random.choice(list(moves.values()))
        if max_player:
            max_eval = -math.inf
            for pieceType, move in moves.items():
                row, file = logic.Utils.index_to_rowfile(int(move[0:2]))
                mrow, mfile = logic.Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(logic.piecesLayout)
                logic.piecesLayout[row][file] = None
                logic.piecesLayout[mrow][mfile] = pieceType
                check = logic.Backend.check_check(logic.black_king_index, False)
                current_eval = Calculations.minimax(depth-1, alpha, beta, False, -max_color, check=check)
                logic.piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval[1] > max_eval:
                    max_eval = current_eval[1]
                    best_move = move
                alpha = max(alpha, current_eval[1])
                if beta <= alpha:
                    break
            # Test callback
            logic.Frontend.test_bot_callback((best_move, max_eval))
            return best_move, max_eval
        else:
            max_eval = math.inf
            for pieceType, move in moves.items():
                row, file = logic.Utils.index_to_rowfile(int(move[0:2]))
                mrow, mfile = logic.Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(logic.piecesLayout)
                logic.piecesLayout[row][file] = None
                logic.piecesLayout[mrow][mfile] = pieceType
                logic.Utils.pretty_print_position()
                check = logic.Backend.check_check(logic.white_king_index, True)
                current_eval = Calculations.minimax(depth-1, alpha, beta, True, -max_color, check=check)
                logic.piecesLayout = deepcopy(tmpPiecesLayout)
                if current_eval[1] < max_eval:
                    max_eval = current_eval[1]
                    best_move = move
                beta = min(beta, current_eval[1])
                if beta <= alpha:
                    break
            # Test callback
            logic.Frontend.test_bot_callback((best_move, max_eval))
            return best_move, max_eval

    def calculate_score(layout):
        white_score, black_score = 0, 0
        for row in layout:
            for el in row:
                if issubclass(type(el), (w.Queen, w.Rook, w.Knight, w.Bishop, w.Pawn)):
                    white_score += weights[type(el)]
                elif issubclass(type(el), (b.Queen, b.Rook, b.Knight, b.Bishop, b.Pawn)):
                    black_score += weights[type(el)]
        return white_score, black_score
    
    def evaluation(color):
        white_eval, black_eval = Calculations.calculate_score(logic.piecesLayout)

        piecesTypesList:list = Misc.piecesTypesList()
        white_mat_nopawns = white_eval - piecesTypesList.count(w.Pawn) * weights[w.Pawn]
        black_mat_nopawns = black_eval - piecesTypesList.count(b.Pawn) * weights[b.Pawn]
        print(f'Amount of pawns. White: {piecesTypesList.count(w.Pawn)}, black: {piecesTypesList.count(b.Pawn)}')
        whiteEndgamePhaseWeight = Calculations.endgameWeight(white_mat_nopawns)
        blackEndgamePhaseWeight = Calculations.endgameWeight(black_mat_nopawns)

        white_eval += Calculations.evaluate_piece_square_tables(True, whiteEndgamePhaseWeight)
        black_eval += Calculations.evaluate_piece_square_tables(False, blackEndgamePhaseWeight)
        return (white_eval - black_eval)*color

    # TODO: It should be [0,1]. Take start weight into account.
    # Weight should be startWeight-weight/multiplier
    def endgameWeight(mat_nopawns):
        mat_less_than_start = MATERIAL_START - mat_nopawns
        mat_endgame_start = MATERIAL_START - ENDGAME_MATERIAL_START
        return max(mat_less_than_start/mat_endgame_start, 1)
    
    def evaluate_piece_square_tables(white, endgameWeight):
        # TODO: Endgame blend pawn table
        value = 0
        white_pieces, black_pieces = logic.Backend.black_and_white_pieces_list()
        for piece in (white_pieces if white else black_pieces):
            row, file = logic.Utils.button_to_rowfile(piece)
            pieceType = type(logic.piecesLayout[row][file])
            if white:
                index = logic.Utils.rowfile_to_index(7-row, file)
            else:
                index = int(piece.text)-1
            if issubclass(pieceType, (w.King, b.King)):
                tables = piece_square_tables[pieceType]
                value += Misc.lerpArrays(tables[0], tables[1], endgameWeight)[index]
                continue
            value += piece_square_tables[pieceType][index]
        return value

class Misc():
    def all_legal_moves(max_player):
        white_pieces, black_pieces = logic.Backend.black_and_white_pieces_list()
        moves = {}
        for el in (white_pieces if max_player else black_pieces):
            row, file = logic.Utils.button_to_rowfile(el)
            pieceType = logic.piecesLayout[row][file]
            moves.update({pieceType: move for move in logic.Backend.legal_moves(el)})
        return moves

    def piecesTypesList():
        li = []
        for row in logic.piecesLayout:
            for square in row:
                li.append(type(square))
        return li
    
    def lerpArrays(a1:list, a2:list, t:float):
        end = []
        for i, el in enumerate(a1):
            end.append(el + t*(a2[i]-el))
        return end