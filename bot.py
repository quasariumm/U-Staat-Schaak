import logic
from pieces import White as w
from pieces import Black as b

import math, random, time

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
    b.Pawn: 100,
    w.King: 0,
    b.King: 0
}
piece_bitboards = [
    'white_king_bitboard', 'black_king_bitboard',
    'white_queen_bitboard', 'black_queen_bitboard',
    'white_bishop_bitboard', 'black_bishop_bitboard',
    'white_knight_bitboard', 'black_knight_bitboard',
    'white_rook_bitboard', 'black_rook_bitboard',
    'white_pawn_bitboard', 'black_pawn_bitboard'
]

ENDGAME_MATERIAL_START = 2 * weights[w.Rook] + weights[w.Bishop] + weights[w.Knight]
MATERIAL_START = 2 * weights[w.Rook] + 2 * weights[w.Bishop] + 2 * weights[w.Knight] + weights[w.Queen]

# https://www.chessprogramming.org/Simplified_Evaluation_Function
pawn_square_table = [
    [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5,  10, 25, 25, 10,  5,  5,
        0,  0,  0,  20, 20,  0,  0,  0,
        5, -5, -10,  0,  0,-10, -5,  5,
        5, 10, 10, -20,-20, 10, 10,  5,
        0,  0,  0,   0,  0,  0,  0,  0
    ],
    [ # Endgame
        0,   0,  0,  0,  0,  0,  0,  0,
        80, 80, 80, 80, 80, 80, 80, 80,
        50, 50, 50, 50, 50, 50, 50, 50,
        30, 30, 30, 30, 30, 30, 30, 30,
        20, 20, 20, 20, 20, 20, 20, 20,
        10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10,
        0,   0,  0,  0,  0,  0,  0,  0,
    ]
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
    [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20
    ],
    [ # Endgame
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
    def minimax(depth:int, alpha:float, beta:float, max_player:bool, max_color:int, check:bool, begin_d:int, lastmove:int=None, linestr:str='') -> tuple[str|int|None, float]:
        if depth == 0:
            return None, Calculations.evaluation(max_color)
        moves = logic.Backend.get_all_legal_moves(max_player, last_move=lastmove, checkk=check)
        if lastmove:
            _, fi, _ = logic.Utils.move_to_fi_ti_flag(lastmove)
            pieceClass = logic.Utils.get_piece_type(fi)()
            new_format = logic.Frontend.move_other_format(lastmove, pieceClass)
        moves = Calculations.moveOrdering(moves)
        if lastmove:
            mate, draw = logic.Backend.mate_and_draw(lastmove)
            if mate:
                return depth, math.inf * (WHITE if max_player else BLACK)
            if draw != '':
                return draw, 0
        best_move = random.choice(moves)
        if max_player:
            max_eval = -math.inf
            for move in moves:
                fi, ti, flag = logic.Utils.move_to_fi_ti_flag(move)
                linestrr = linestr + f'-{fi:02},{ti:02},{flag},{"+" if check else "_"}'
                try:
                    sname, tname = logic.Backend.make_unmake_move(fi, ti, flag, True)
                except:
                    print(fi, ti, flag)
                    logic.Utils.pretty_print_position()
                logic.white_total_bitboard = logic.white_bishop_bitboard | logic.white_king_bitboard | logic.white_knight_bitboard | logic.white_rook_bitboard | logic.white_queen_bitboard | logic.white_pawn_bitboard
                logic.black_total_bitboard = logic.black_bishop_bitboard | logic.black_king_bitboard | logic.black_knight_bitboard | logic.black_rook_bitboard | logic.black_queen_bitboard | logic.black_pawn_bitboard
                logic.attacking_bitboard = 0
                logic.pin_bitboard = 0
                logic.king_attack_bitboard = 0
                logic.Backend.attack_pin_bitboard(False)
                try:
                    checkk = logic.Backend.check_index_overlap(logic.attacking_bitboard, int(math.log2(logic.black_king_bitboard)))
                    logic.check = checkk
                except ValueError:
                    print(logic.black_king_bitboard)
                    print(f'{lastmove:016b}')
                    print(linestrr)
                    logic.Utils.pretty_print_position()
                _,current_eval = Calculations.minimax(depth-1, alpha, beta, False, -max_color, check=checkk, begin_d=begin_d, lastmove=move, linestr=linestrr)
                logic.Backend.make_unmake_move(fi, ti, flag, True, sname=sname, tname=tname)
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move

                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
        else:
            max_eval = math.inf
            for move in moves:
                fi, ti, flag = logic.Utils.move_to_fi_ti_flag(move)
                linestrr = linestr + f'-{fi:02},{ti:02},{flag},{"+" if check else "_"}'
                try:
                    sname, tname = logic.Backend.make_unmake_move(fi, ti, flag, False)
                except:
                    print(fi, ti, flag)
                    logic.Utils.pretty_print_position()
                logic.white_total_bitboard = logic.white_bishop_bitboard | logic.white_king_bitboard | logic.white_knight_bitboard | logic.white_rook_bitboard | logic.white_queen_bitboard | logic.white_pawn_bitboard
                logic.black_total_bitboard = logic.black_bishop_bitboard | logic.black_king_bitboard | logic.black_knight_bitboard | logic.black_rook_bitboard | logic.black_queen_bitboard | logic.black_pawn_bitboard
                logic.attacking_bitboard = 0
                logic.pin_bitboard = 0
                logic.king_attack_bitboard = 0
                logic.Backend.attack_pin_bitboard(True)
                try:
                    checkk = logic.Backend.check_index_overlap(logic.attacking_bitboard, int(math.log2(logic.white_king_bitboard)))
                    logic.check = checkk
                except ValueError:
                    print(logic.black_king_bitboard)
                    print(f'{lastmove:016b}')
                    print(linestrr)
                    logic.Utils.pretty_print_position()
                _,current_eval = Calculations.minimax(depth-1, alpha, beta, True, -max_color, check=checkk, begin_d=begin_d, lastmove=move, linestr=linestrr)
                logic.Backend.make_unmake_move(fi, ti, flag, False, sname=sname, tname=tname)
                if current_eval < max_eval:
                    max_eval = current_eval
                    best_move = move

                beta = min(beta, current_eval)
                if beta <= alpha:
                    break

        if depth == begin_d:
            # Make the move
            fi, ti, flag = logic.Utils.move_to_fi_ti_flag(best_move)
            logic.selected = logic.board[fi]
            logic.tempBackground_color = logic.board[fi].background_color
            if flag[0] not in ['p', 'q']:
                logic.Frontend.move(logic.board[fi], logic.board[ti])
            else:
                logic.promotionStatus = 1
                logic.promotionType = flag[-1]
                logic.Frontend.promotionMove(logic.board[fi], logic.board[ti], None, bot_move=True)
            logic.bot_move = False
            piece_type = logic.Utils.get_piece_type(fi)()
            new_format = logic.Frontend.move_other_format(best_move, piece_type)
            print(new_format, max_eval)
        return best_move, max_eval

    def calculate_score(piecesTypesList:list):
        white_score, black_score = 0, 0
        for piece in piecesTypesList:
            if piece is None:
                continue
            if issubclass(piece, (w.Queen, w.Rook, w.Knight, w.Bishop, w.Pawn)):
                white_score += weights[piece]
            elif issubclass(piece, (b.Queen, b.Rook, b.Knight, b.Bishop, b.Pawn)):
                black_score += weights[piece]
        return white_score, black_score
    
    def evaluation(color) -> int:
        piecesTypesList:list = Misc.piecesTypesList()
        white_eval, black_eval = Calculations.calculate_score(piecesTypesList)

        white_mat_nopawns = white_eval - piecesTypesList.count(w.Pawn) * weights[w.Pawn]
        black_mat_nopawns = black_eval - piecesTypesList.count(b.Pawn) * weights[b.Pawn]
        whiteEndgamePhaseWeight = Calculations.endgameWeight(white_mat_nopawns)
        blackEndgamePhaseWeight = Calculations.endgameWeight(black_mat_nopawns)

        white_eval += Calculations.evaluate_piece_square_tables(True, whiteEndgamePhaseWeight)
        black_eval += Calculations.evaluate_piece_square_tables(False, blackEndgamePhaseWeight)
        return (white_eval - black_eval)*color

    def endgameWeight(mat_nopawns):
        mat_less_than_start = MATERIAL_START - mat_nopawns
        mat_endgame_start = MATERIAL_START - ENDGAME_MATERIAL_START
        return min(mat_less_than_start/mat_endgame_start, 1)
    
    def evaluate_piece_square_tables(white, endgameWeight):
        value = 0
        white_pieces, black_pieces = logic.Backend.black_and_white_pieces_list()
        for piece in (white_pieces if white else black_pieces):
            row, file = logic.Utils.button_to_rowfile(piece)
            pieceType = logic.Utils.get_piece_type(8*row+file)
            if white:
                index = logic.Utils.rowfile_to_index(7-row, file)
            else:
                index = int(piece.text)-1
            if issubclass(pieceType, (w.King, b.King)):
                tables = king_square_table
                value += Misc.lerpArrays(tables[0], tables[1], endgameWeight)[index]
                continue
            elif issubclass(pieceType, (w.Pawn, b.Pawn)):
                tables = pawn_square_table
                value += Misc.lerpArrays(tables[0], tables[1], endgameWeight)[index]
                continue
            value += piece_square_tables[pieceType][index]
        return value
    
    def moveOrdering(moves):
        moveScoreGuesses = {}
        for move in moves:
            moveScoreGuesses[move] = 0
            fi, ti, flag = logic.Utils.move_to_fi_ti_flag(move)
            pieceType = logic.Utils.get_piece_type(fi)
            movePieceType = logic.Utils.get_piece_type(ti)
            if movePieceType is not None and not issubclass(movePieceType, (w.King, b.King)):
                moveScoreGuesses[move] = 10 * weights[pieceType] - weights[movePieceType]
            if flag in ['pq', 'pr', 'pb', 'pn', 'qq', 'qr', 'qb', 'qn']:
                moveScoreGuesses[move] += weights[w.Queen if flag[-1] == 'q' else w.Rook if flag[-1] == 'r' else w.Bishop if flag[-1] == 'b' else w.Knight]
        sorted_moves = list(dict(sorted(moveScoreGuesses.items(), key=lambda item: item[1])).keys())
        return sorted_moves

class Misc():
    def piecesTypesList():
        li = []
        for i in range(64):
            li.append(logic.Utils.get_piece_type(i))
        return li
    
    def lerpArrays(a1:list, a2:list, t:float):
        end = []
        for i, el in enumerate(a1):
            end.append(el + t*(a2[i]-el))
        return end