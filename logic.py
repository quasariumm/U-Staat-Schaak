import math,os
from collections import Counter
from copy import deepcopy
from threading import Thread, Event

from pieces import White as w
from pieces import Black as b
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from app import board_prim, board, piecesLayout, ChessPromotionUI
from pieces import White as w
from pieces import Black as b

from bot import Calculations

selected : Button = None
tempBackground_color = []
white_to_move = True
legal_moves_cache = None

# Castling requirements
white_krook_moved = False
white_qrook_moved = False
white_king_moved = False
black_krook_moved = False
black_qrook_moved = False
black_king_moved = False

check = False
mate = False
white_king_index = 4
black_king_index = 60

#      __    _ __  __                         __    
#     / /_  (_) /_/ /_  ____  ____ __________/ /____
#    / __ \/ / __/ __ \/ __ \/ __ `/ ___/ __  / ___/
#   / /_/ / / /_/ /_/ / /_/ / /_/ / /  / /_/ (__  ) 
#  /_.___/_/\__/_.___/\____/\__,_/_/   \__,_/____/  
#                                                   
white_king_bitboard = 0x0000000000000000
white_queen_bitboard = 0x0000000000000000
white_bishop_bitboard = 0x0000000000000000
white_knight_bitboard = 0x0000000000000000
white_rook_bitboard = 0x0000000000000000
white_pawn_bitboard = 0x0000000000000000
black_king_bitboard = 0x0000000000000000
black_queen_bitboard = 0x0000000000000000
black_bishop_bitboard = 0x0000000000000000
black_knight_bitboard = 0x0000000000000000
black_rook_bitboard = 0x0000000000000000
black_pawn_bitboard = 0x0000000000000000

# Moves format: {<algebraic chess notation>: move with indecies}
# ex. {'e4': '1228n'}
moves_list = {}
promotionStatus = 0
promotionType = ''
promotionEvent = Event()

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        global white_to_move
        row, file = Utils.button_to_rowfile(button)

        if selected != None :
            if selected != button:
                if (selected.image.source[-7] == 'w' and white_to_move) or (selected.image.source[-7] == 'b' and not white_to_move):
                    code = Frontend.move(selected, button)
                    if code == 200:
                        return
    	    
        if selected == None and piecesLayout[row][file] != None:
            selected = button
            tempBackground_color = selected.background_color
            r,g,bl,a = selected.background_color
            selected.background_color = [r*0.5, g, bl, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, bl, a]
            if (issubclass(type(piecesLayout[row][file]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)) and white_to_move) or (issubclass(type(piecesLayout[row][file]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen)) and not white_to_move):
                Frontend.show_legal_move_indicators(button)
        elif piecesLayout[row][file] == None and selected == None:
            pass
        elif selected.text == button.text or piecesLayout[row][file] == None:
            selected.background_color = tempBackground_color
            selected = None
            Frontend.clear_legal_moves_indicators()
        else:
            Frontend.clear_legal_moves_indicators()
            selected.background_color = tempBackground_color
            selected = button
            tempBackground_color = selected.background_color
            r,g,bl,a = selected.background_color
            selected.background_color = [r*0.5, g, bl, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, bl, a]
            if (issubclass(type(piecesLayout[row][file]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)) and white_to_move) or (issubclass(type(piecesLayout[row][file]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen)) and not white_to_move):
                Frontend.show_legal_move_indicators(button)
        
    def move(check_piece, dest: Button):
        global selected
        global tempBackground_color
        global white_to_move
        global check, mate, white_king_index, black_king_index
        global white_king_moved, white_krook_moved, white_qrook_moved, black_king_moved, black_krook_moved, black_qrook_moved
        global legal_moves_cache
        row, file = Utils.button_to_rowfile(check_piece)
        destrow, destfile = Utils.button_to_rowfile(dest)
        if destrow == 7 and white_to_move or destrow == 0 and not white_to_move:
            # Show the promotion GUI
            promoteUI = ChessPromotionUI()
            # TODO: Content not displaying
            popup = Popup(title='Select piece type', content=promoteUI, size_hint=(0.25, 0.35))
            promoteUI.change_color(piecesLayout[row][file])
            popup.bind(on_dismiss=promoteUI.cancel)
            popup.open()
            Thread(target=Frontend.promotionMove, args=[check_piece, dest, popup]).start()
            return 200
        pieceType = piecesLayout[row][file]

        moves = legal_moves_cache
        moves_otherformat = [m[0:4] for m in moves]
        i1 = int(selected.text)-1
        i2 = int(dest.text)-1
        move_from = f'0{i1}' if i1<10 else str(i1)
        move_to = f'0{i2}' if i2<10 else str(i2)
        move = move_from + move_to
        if moves:
            if move in moves_otherformat:
                movee = moves[moves_otherformat.index(move)]
                if movee[4] == 'e':
                    pass
                elif movee[4] == 'k':
                    movement = pieceType.movement[1][0]
                    dest = board[8*(row+movement[1])+(file+movement[0])]
                    dest.image.source = check_piece.image.source
                    check_piece.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                    movement = pieceType.movement[1][1]
                    rook = board[8*(row+movement[1])+(file+movement[0])]
                    board[8*(row)+(file+1)].image.source = rook.image.source
                    rook.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                elif movee[4] == 'q':
                    movement = pieceType.movement[0][0]
                    dest = board[8*(row+movement[1])+(file+movement[0])]
                    dest.image.source = check_piece.image.source
                    check_piece.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                    movement = pieceType.movement[0][1]
                    rook = board[8*(row+movement[1])+(file+movement[0])]
                    board[8*(row)+(file-1)].image.source = rook.image.source
                    rook.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                else:
                    dest.image.source = selected.image.source 
                    selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                selected.background_color = tempBackground_color
                selected = None
                white_to_move = not white_to_move
                # Check if rook or king has moved
                if isinstance(pieceType, w.King):
                    white_king_index = int(dest.text)-1
                    if not white_king_moved:
                        white_king_moved = True
                elif isinstance(pieceType, b.King):
                    black_king_index = int(dest.text)-1
                    if not black_king_moved:
                        black_king_moved = True
                elif isinstance(pieceType, w.Rook):
                    if file == 0 and not white_qrook_moved:
                        white_qrook_moved = True
                    elif file == 7 and not white_krook_moved:
                        white_krook_moved = True
                elif isinstance(pieceType, b.Rook):
                    if file == 0 and not black_qrook_moved:
                        black_qrook_moved = True
                    elif file == 7 and not black_krook_moved:
                        black_krook_moved = True
                # If one of the rooks is captured, update the rook_moved values
                # Otherwise the king can castle with a nonexistent rook
                if isinstance(piecesLayout[destrow][destfile], w.Rook):
                    if destfile == 0 and not white_qrook_moved:
                        white_qrook_moved = True
                    elif destfile == 7 and not white_krook_moved:
                        white_krook_moved = True
                elif isinstance(piecesLayout[destrow][destfile], b.Rook):
                    if destfile == 0 and not black_qrook_moved:
                        black_qrook_moved = True
                    elif destfile == 7 and not black_krook_moved:
                        black_krook_moved = True
                Backend.update_pieces_layout()
                Backend.update_bitboards()
                check = Backend.check_check(white_king_index if white_to_move else black_king_index, white_to_move)
                print('check' if check else 'not check')
                if check:
                    mate = Backend.check_mate(white_king_index if white_to_move else black_king_index, white_to_move)
                    print('mate' if mate else 'not mate')
                Frontend.clear_legal_moves_indicators()

                # Just to test
                print(Calculations.minimax(4, -math.inf, math.inf, True if white_to_move else False))
                return 200
            else:
                return 404
    
    def reset_event():
        global promotionStatus, promotionEvent
        promotionEvent.clear()
        promotionStatus = 0
    
    def promotionMove(check_piece, dest:Button, popup:Popup):
        global selected
        global tempBackground_color
        global white_to_move
        global legal_moves_cache
        global promotionStatus, promotionEvent
        promotionEvent.wait()
        if promotionStatus == 2:
            popup.dismiss()
            Frontend.reset_event()
            return 418
        popup.dismiss()
        Frontend.reset_event()
        moves = legal_moves_cache
        moves_otherformat = [m[0:4] for m in moves]
        i1 = int(selected.text)-1
        i2 = int(dest.text)-1
        move_from = f'0{i1}' if i1<10 else str(i1)
        move_to = f'0{i2}' if i2<10 else str(i2)
        move = move_from + move_to
        if moves:
            if move in moves_otherformat:
                dest.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\Default\\{'w' if white_to_move else 'b'}{promotionType}n.png"
                selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                selected.background_color = tempBackground_color
                selected = None
                white_to_move = not white_to_move
                Backend.update_pieces_layout()
                Backend.update_bitboards()
                check = Backend.check_check(white_king_index if white_to_move else black_king_index, white_to_move)
                print('check' if check else 'not check')
                if check:
                    mate = Backend.check_mate(white_king_index if white_to_move else black_king_index, white_to_move)
                    print('mate' if mate else 'not mate')
                Frontend.clear_legal_moves_indicators()
                return 200
        else:
            return 404

    def show_legal_move_indicators(button):
        global legal_moves_cache
        moves = Backend.legal_moves(button=button)
        legal_moves_cache = moves
        if moves:
            for move in moves:
                board[int(move[2:4])].background_normal = os.path.dirname(__file__) + '\\data\\img\\legal_capture.png'

    def clear_legal_moves_indicators():
        for square in board:
            square.background_normal = ''
            square.background_down = ''

class Backend():
    # NOTE: Legal move format
    #   2 chars    2 chars  1 char
    # <index from><index to><type>
    # Types:
    # 'n' - normal
    # 'c' - capture
    # 'e' - en passant
    # 'k' or 'q' - King- or Queenside castling
    def legal_moves(button:Button=None, rowfile:tuple=None, src:str=None, check_check=False):
        global check, piecesLayout, white_to_move
        if button:
            row, file = Utils.button_to_rowfile(button)
            colorstr = button.image.source[-7]
        else:
            row, file = rowfile
            colorstr = src[-7]

        pieceType = piecesLayout[row][file]
        legalmoves = []

        # Pawn specific
        if isinstance(pieceType, w.Pawn) or isinstance(pieceType, b.Pawn):
            # En passant TODO (this will be such a pain in the ass to make)

            # Capture
            try:
                tmpRow, tmpFile = row+pieceType.movement[2][0][1], file+pieceType.movement[2][0][0]
                if (piecesLayout[tmpRow][tmpFile] != None) and not (tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0):
                    if (colorstr == 'b' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)))\
                    or (colorstr == 'w' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen))):
                        legalmoves.append([pieceType.movement[2][0], 'c'])
                tmpRow, tmpFile = row+pieceType.movement[3][0][1], file+pieceType.movement[3][0][0]
                if (piecesLayout[tmpRow][tmpFile] != None) and not (tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0):
                    if (colorstr == 'b' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)))\
                    or (colorstr == 'w' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen))):
                        legalmoves.append([pieceType.movement[3][0], 'c'])
            except Exception as e:
                pass # Probably IndexError
            # First move (only if no piece is in the way of the normal move)
            if (isinstance(pieceType, w.Pawn) and row == 1) or (isinstance(pieceType, b.Pawn) and row == 6):
                if piecesLayout[row + pieceType.movement[0][0][1]][file] == None\
                and piecesLayout[row + pieceType.movement[1][0][1]][file] == None:
                    legalmoves.append([pieceType.movement[0][0], 'n']) # First move
            # If nothing is blocking, add the normal move
            try:
                if piecesLayout[row + pieceType.movement[1][0][1]][file] == None:
                    legalmoves.append([pieceType.movement[1][0], 'n'])
            except:
                pass
        # King specific
        elif isinstance(pieceType, w.King) or isinstance(pieceType, b.King):
            king_moves = []
            try:
                # Castling kingside
                if (isinstance(pieceType, w.King) and not white_king_moved and not white_krook_moved and piecesLayout[row][file+1] == None and piecesLayout[row][file+2] == None)\
                or (isinstance(pieceType, b.King) and not black_king_moved and not black_krook_moved and piecesLayout[row][file+1] == None and piecesLayout[row][file+2] == None):
                    king_moves.append([pieceType.movement[1][0], 'k'])
                    king_moves.append([pieceType.movement[1][1], 'k'])
                # Castle queenside
                if (isinstance(pieceType, w.King) and not white_king_moved and not white_qrook_moved and piecesLayout[row][file-1] == None and piecesLayout[row][file-2] == None and piecesLayout[row][file-3] == None)\
                or (isinstance(pieceType, b.King) and not black_king_moved and not black_qrook_moved and piecesLayout[row][file-1] == None and piecesLayout[row][file-2] == None and piecesLayout[row][file-3] == None):
                    king_moves.append([pieceType.movement[0][0], 'q'])
                    king_moves.append([pieceType.movement[0][1], 'q'])
            except:
                print('Thou shalt not be castling this move.')

            for i in range(2,10):
                tmpmove = pieceType.movement[i][0]
                tmpRow = row + tmpmove[1]
                tmpFile = file + tmpmove[0]
                if not (tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0):
                    if (piecesLayout[tmpRow][tmpFile] == None):
                        king_moves.append([tmpmove, 'n'])
                    if (colorstr == 'b' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)))\
                    or (colorstr == 'w' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen))):
                        king_moves.append([tmpmove, 'c'])
            return Backend.check_king_legal_moves(Backend.format_legal_moves(king_moves, row, file), pieceType)
        else:
            for direction in pieceType.movement:
                for option in direction:
                    tmpRow = row + option[1]
                    tmpFile = file + option[0]
                    if (tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0):
                        break
                    else:
                        if (piecesLayout[tmpRow][tmpFile] == None):
                            legalmoves.append([option, 'n'])
                        elif (colorstr == 'b' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)))\
                        or (colorstr == 'w' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen))):
                            legalmoves.append([option, 'c'])
                            break
                        else:
                            break

        if len(legalmoves) > 0:
            legalmoves = Backend.format_legal_moves(legalmoves, row, file)
        
        # If the king is in check, only accept moves that lead the king into not being checked anymore
        # If the remaining list is empty, it's mate
        if legalmoves and not check_check:
            legalmovescopy = deepcopy(legalmoves)
            for move in legalmoves:
                mrow, mfile = Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(piecesLayout)
                piecesLayout[row][file] = None
                piecesLayout[mrow][mfile] = pieceType
                tstcheck = Backend.check_check(white_king_index if white_to_move else black_king_index, white_to_move)
                piecesLayout = deepcopy(tmpPiecesLayout)
                if tstcheck:
                    legalmovescopy.remove(move)
            legalmoves = deepcopy(legalmovescopy)
        return legalmoves
    
    def format_legal_moves(legalmoves, row, file):
        well_formatted = []
        for el in legalmoves:
            move = el[0]
            moveType = el[1]
            i = 8*(row+move[1]) + (file+move[0])
            move_from = f'0{8*row+file}' if 8*row+file<10 else str(8*row+file)
            move_to = f'0{i}' if i<10 else str(i)
            well_formatted.append(move_from + move_to + moveType)
        return well_formatted
    
    def black_and_white_pieces_list():
        white_pieces = []
        black_pieces = []
        for i,row in enumerate(piecesLayout):
            for j,square in enumerate(row):
                if issubclass(type(square), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)):
                    white_pieces.append(board[8*i+j])
                elif issubclass(type(square), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen)):
                    black_pieces.append(board[8*i+j])
        return white_pieces, black_pieces
    
    def check_check(king_index, white_move):
        global piecesLayout
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        for piece in (black_pieces if white_move else white_pieces):
            row, file = Utils.button_to_rowfile(piece)
            if not issubclass(type(piecesLayout[row][file]), (w.King, b.King)):
                moves = Backend.legal_moves(button=piece, check_check=True)
                if moves:
                    if king_index in [int(m[2:4]) for m in moves]:
                        return True
        return False

    # TODO: wrong result with scholar's mate
    def check_mate(king_index, white_move):
        has_legal_moves = []
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        for piece in (white_pieces if white_move else black_pieces):
            moves = Backend.legal_moves(button=piece)
            if moves:
                has_legal_moves.append(True)
        if check and len(has_legal_moves) == 0:
            return True
        return False
    
    def reduce_king_legal_moves(pieces, moves_list, moves_dict, reduced):
        for piece in pieces:
            row, file = Utils.button_to_rowfile(piece)
            if (isinstance(piecesLayout[row][file], w.King) and white_to_move)\
            or (isinstance(piecesLayout[row][file], b.King) and not white_to_move):
                continue
            moves = Backend.legal_moves(button=piece)
            if moves:
                moves = [m[2:4] for m in moves]
                intersection = [i for i,j in Counter(moves + reduced).items() if j > 1]
                if intersection:
                    for m in intersection:
                        reduced.remove(m)
                        moves_list.remove(moves_dict[m])
                        del moves_dict[m]
        return moves_list
    
    def check_king_legal_moves(moves_list:list, pieceType):
        global piecesLayout
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        if moves_list:
            reduced_moves_list = [m[2:4] for m in moves_list]
            moves_dict = {key: value for key, value in zip(reduced_moves_list, moves_list)}
            pieces_list = black_pieces if isinstance(pieceType, w.King) else white_pieces
            moves_list = Backend.reduce_king_legal_moves(pieces_list, moves_list, moves_dict, reduced_moves_list)
        if (isinstance(pieceType, w.King) and not white_to_move)\
        or (isinstance(pieceType, b.King) and white_to_move):
            return moves_list
        # Check if the king can capture any of the opponent's piece
        # If so, look at that situation and look if a piece of the opponent can capture your king
        # If that is the case, the king can't capture said piece
        krow, kfile = Utils.index_to_rowfile(white_king_index if white_to_move else black_king_index)
        moves_listcopy = deepcopy(moves_list)
        for m in moves_list:
            button = board[int(m[2:4])]
            row, file = Utils.button_to_rowfile(button)
            if (button.image.source[-7] == 'b' and isinstance(pieceType, w.King))\
            or (button.image.source[-7] == 'w' and isinstance(pieceType, b.King)):
                for piece in (black_pieces if isinstance(pieceType, w.King) else white_pieces):
                    if (isinstance(piecesLayout[row][file], w.King) and white_to_move)\
                    or (isinstance(piecesLayout[row][file], b.King) and not white_to_move):
                        continue
                    tmpPiecesLayout = deepcopy(piecesLayout)
                    piecesLayout[krow][kfile] = None
                    piecesLayout[row][file] = w.King() if white_to_move else b.King()
                    moves = Backend.legal_moves(piece)
                    piecesLayout = deepcopy(tmpPiecesLayout)
                    if not moves:
                        continue
                    if (white_king_index if isinstance(pieceType, w.King) else black_king_index) in [int(n[2:4]) for n in moves]:
                        moves_listcopy.remove(m)

        return deepcopy(moves_listcopy)

    def update_bitboards():
        global white_bishop_bitboard, white_king_bitboard, white_knight_bitboard, white_pawn_bitboard, white_queen_bitboard, white_rook_bitboard, black_bishop_bitboard, black_king_bitboard, black_knight_bitboard, black_pawn_bitboard, black_queen_bitboard, black_rook_bitboard
        for el in [white_bishop_bitboard, white_king_bitboard, white_knight_bitboard, white_pawn_bitboard, white_queen_bitboard, white_rook_bitboard, black_bishop_bitboard, black_king_bitboard, black_knight_bitboard, black_pawn_bitboard, black_queen_bitboard, black_rook_bitboard]:
            el = 0x0000000000000000
        for i,row in enumerate(piecesLayout):
            for j,square in enumerate(row):
                if square == None:
                    continue
                else:
                    pieceType = square
                    if isinstance(pieceType, w.Pawn):
                        white_pawn_bitboard = Utils.switch_bit_on(white_pawn_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Pawn):
                        black_pawn_bitboard = Utils.switch_bit_on(black_pawn_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Rook):
                        white_rook_bitboard = Utils.switch_bit_on(white_rook_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Rook):
                        black_rook_bitboard = Utils.switch_bit_on(black_rook_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Knight):
                        white_knight_bitboard = Utils.switch_bit_on(white_knight_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Knight):
                        black_knight_bitboard = Utils.switch_bit_on(black_knight_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Bishop):
                        white_bishop_bitboard = Utils.switch_bit_on(white_bishop_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Bishop):
                        black_bishop_bitboard = Utils.switch_bit_on(black_bishop_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Queen):
                        white_queen_bitboard = Utils.switch_bit_on(white_queen_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Queen):
                        black_queen_bitboard = Utils.switch_bit_on(black_queen_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.King):
                        white_king_bitboard = Utils.switch_bit_on(white_king_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.King):
                        black_king_bitboard = Utils.switch_bit_on(black_king_bitboard, 8*i+j)
        # print('wb: ' + bin(white_bishop_bitboard))
        # print('wk: ' + bin(white_king_bitboard))
        # print('wn: ' + bin(white_knight_bitboard))
        # print('wp: ' + bin(white_pawn_bitboard))
        # print('wq: ' + bin(white_queen_bitboard))
        # print('wr: ' + bin(white_rook_bitboard))
        # print('bb: ' + bin(black_bishop_bitboard))
        # print('bk: ' + bin(black_king_bitboard))
        # print('bn: ' + bin(black_knight_bitboard))
        # print('bp: ' + bin(black_pawn_bitboard))
        # print('bq: ' + bin(black_queen_bitboard))
        # print('br: ' + bin(black_rook_bitboard))
    def update_pieces_layout():
        dictt={
            'wk': w.King(),
            'wp': w.Pawn(),
            'wn': w.Knight(),
            'wb': w.Bishop(),
            'wr': w.Rook(),
            'wq': w.Queen(),
            'bk': b.King(),
            'bp': b.Pawn(),
            'bn': b.Knight(),
            'bb': b.Bishop(),
            'br': b.Rook(),
            'bq': b.Queen(),
            'pt': None}
        for i,square in enumerate(board):
            piece = dictt[square.image.source[-7:-5]]
            row = math.floor((int(square.text)-1)/8)
            file = (int(square.text)-1)%8
            piecesLayout[row][file]= piece

class Utils():
    def switch_bit_on(board, i):
        return board | 2**i

    def button_to_rowfile(button):
        return math.floor((int(button.text)-1)/8), (int(button.text)-1)%8

    def index_to_rowfile(i):
        return math.floor(i/8), i%8
    
    def rowfile_to_index(row, file):
        return 8*row+file