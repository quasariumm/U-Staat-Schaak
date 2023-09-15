import math,os
from pieces import White as w
from pieces import Black as b
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button

from app import board_prim, board, piecesLayout
from pieces import White as w
from pieces import Black as b

selected : Button = None
tempBackground_color = []
white_to_move = True

# Castling requirements
white_krook_moved = False
white_qrook_moved = False
white_king_moved = False
black_krook_moved = False
black_qrook_moved = False
black_king_moved = False

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

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        global white_to_move
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8

        if selected != None :
            if selected != button:
                if (selected.image.source[-7] == 'w' and white_to_move) or (selected.image.source[-7] == 'b' and not white_to_move):
                    Frontend.move(selected, button)
                    return
    	    
        if selected == None and piecesLayout[row][file] != None:
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]
            Frontend.show_legal_move_indicators(selected)
        elif piecesLayout[row][file] == None and selected == None:
            pass
        elif selected.text == button.text or piecesLayout[row][file] == None:
            selected.background_color = tempBackground_color
            selected = None
            Frontend.clear_legal_moves_indicators()
        else:
            Frontend.clear_legal_moves_indicators()
            selected.background_color = tempBackground_color
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]
            Frontend.show_legal_move_indicators(selected)
        
    def move(check_piece, piece: Button):
        global selected
        global tempBackground_color
        global white_to_move
        moves = Backend.legal_moves(check_piece)
        i1 = int(selected.text)-1
        i2 = int(piece.text)-1
        move_from = f'0{i1}' if i1<10 else str(i1)
        move_to = f'0{i2}' if i2<10 else str(i2)
        move = move_from + move_to
        if moves:
            for movee in moves:
                if move == movee[0:4]:
                    piece.image.source = selected.image.source 
                    selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                    selected.background_color = tempBackground_color
                    selected = None
                    white_to_move = not white_to_move
                    Backend.update_pieces_layout()
                    Backend.update_bitboards()
                    Frontend.clear_legal_moves_indicators()

    def show_legal_move_indicators(button):
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8
        moves = Backend.legal_moves(button)
        for move in moves:
            board[int(move[2:3])].background_normal = os.path.dirname(__file__) + '\\data\\img\\legal_capture.png'

    def clear_legal_moves_indicators():
        for square in board:
            square.background_normal = ''
            square.background_down = ''

class Backend():
    # NOTE: Legal move format
    #   2 chars    2 chars  1 char
    # <index from><index to><type>
    # Types:
    # 'n' - normal/capture
    # 'e' - en passant
    # 'k' or 'q' - King- or Queenside castling
    def legal_moves(button):
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8
        pieceType = piecesLayout[row][file]
        legalmoves = []
        # Pawn specific
        if isinstance(pieceType, w.Pawn) or isinstance(pieceType, b.Pawn):
            # En passant TODO (this will be such a pain in the ass to make)

            # Capture
            if (piecesLayout[row+pieceType.movement[2][0][1]][file+pieceType.movement[2][0][0]] != None):
                legalmoves.append([pieceType.movement[2][0], 'n'])
            elif (piecesLayout[row+pieceType.movement[3][0][1]][file+pieceType.movement[3][0][0]] != None):
                legalmoves.append([pieceType.movement[3][0], 'n'])
            # First move
            if (isinstance(pieceType, w.Pawn) and row == 1) or (isinstance(pieceType, b.Pawn) and row == 6):
                if piecesLayout[row + pieceType.movement[0][0][1]][file] == None:
                    legalmoves.append([pieceType.movement[0][0], 'n']) # First move
            # If nothing is blocking, add the normal move
            if piecesLayout[row + pieceType.movement[1][0][1]][file] == None:
                legalmoves.append([pieceType.movement[1][0], 'n'])
        # King specific
        elif isinstance(pieceType, w.King) or isinstance(pieceType, b.King):
            try:
                # Castling kingside
                if (isinstance(pieceType, w.King) and not white_king_moved and not white_krook_moved and piecesLayout[row][file+1] == None and piecesLayout[row][file+2] == None)\
                or (isinstance(pieceType, b.King) and not black_king_moved and not black_krook_moved and piecesLayout[row][file+1] == None and piecesLayout[row][file+2] == None):
                    legalmoves.append([pieceType.movement[1][0], 'k'])
                    legalmoves.append([pieceType.movement[1][1], 'k'])
                # Castle queenside
                if (isinstance(pieceType, w.King) and not white_king_moved and not white_qrook_moved and piecesLayout[row][file-1] == None and piecesLayout[row][file-2] == None and piecesLayout[row][file-3] == None)\
                or (isinstance(pieceType, b.King) and not black_king_moved and not black_qrook_moved and piecesLayout[row][file-1] == None and piecesLayout[row][file-2] == None and piecesLayout[row][file-3] == None):
                    legalmoves.append([pieceType.movement[0][0], 'q'])
                    legalmoves.append([pieceType.movement[0][1], 'q'])
            except:
                print('Thou shalt not be castling this move.')

            for i in range(2,10):
                tmpmove = pieceType.movement[i][0]
                tmpRow = row + tmpmove[1]
                tmpFile = file + tmpmove[0]
                if not (tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0):
                    if not (piecesLayout[tmpRow][tmpFile] != None):
                        legalmoves.append([tmpmove,'n'])
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
                        else:
                            break
        if len(legalmoves) > 0:
            well_formatted = []
            for el in legalmoves:
                move = el[0]
                moveType = el[1]
                i = 8*(row+move[1]) + (file+move[0])
                move_from = f'0{8*row+file}' if 8*row+file<10 else str(8*row+file)
                move_to = f'0{i}' if i<10 else str(i)
                well_formatted.append(move_from + move_to + moveType)
            return well_formatted
        
    def switch_bit_on(board, i):
        return board | 2**i

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
                        white_pawn_bitboard = Backend.switch_bit_on(white_pawn_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Pawn):
                        black_pawn_bitboard = Backend.switch_bit_on(black_pawn_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Rook):
                        white_rook_bitboard = Backend.switch_bit_on(white_rook_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Rook):
                        black_rook_bitboard = Backend.switch_bit_on(black_rook_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Knight):
                        white_knight_bitboard = Backend.switch_bit_on(white_knight_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Knight):
                        black_knight_bitboard = Backend.switch_bit_on(black_knight_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Bishop):
                        white_bishop_bitboard = Backend.switch_bit_on(white_bishop_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Bishop):
                        black_bishop_bitboard = Backend.switch_bit_on(black_bishop_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.Queen):
                        white_queen_bitboard = Backend.switch_bit_on(white_queen_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.Queen):
                        black_queen_bitboard = Backend.switch_bit_on(black_queen_bitboard, 8*i+j)
                    elif isinstance(pieceType, w.King):
                        white_king_bitboard = Backend.switch_bit_on(white_king_bitboard, 8*i+j)
                    elif isinstance(pieceType, b.King):
                        black_king_bitboard = Backend.switch_bit_on(black_king_bitboard, 8*i+j)
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

