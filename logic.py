import math,os,time
import numpy as np
from collections import Counter
from copy import deepcopy
from threading import Thread, Event

from pieces import White as w
from pieces import Black as b
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivymd.uix.list import OneLineListItem
from kivy.uix.popup import Popup

from app import board_prim, board, piecesLayout, ChessPromotionUI
from pieces import White as w
from pieces import Black as b

from bot import Calculations, Misc, WHITE

movenum=0
move_list = None
list_items=[]

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
white_king_bitboard = 0
white_queen_bitboard = 0
white_bishop_bitboard = 0
white_knight_bitboard = 0
white_rook_bitboard = 0
white_pawn_bitboard = 0
black_king_bitboard = 0
black_queen_bitboard = 0
black_bishop_bitboard = 0
black_knight_bitboard = 0
black_rook_bitboard = 0
black_pawn_bitboard = 0
white_total_bitboard = 0
black_total_bitboard = 0

attacking_bitboard = 0
pin_bitboard = 0

legal_moves_flags = {
    'n': 0b0001,
    'c': 0b0010,
    'e': 0b0011,
    'k': 0b0100,
    'q': 0b0101,
    'pq': 0b0110,
    'pr': 0b0111,
    'pb': 0b1000,
    'pn': 0b1001
}

moves_list = []
promotionStatus = 0
promotionType = ''
promotionEvent = Event()

class Tests():
    def legal_move_time_comparison():
        start = time.time()
        Misc.all_legal_moves()
        print(f'The old method took {time.time()-start:04d} seconds')
        start = time.time()
        Backend.get_all_legal_moves()
        print(f'The bitboard method took {time.time()-start:04d} seconds')

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
        global movenum
        global white_king_moved, white_krook_moved, white_qrook_moved, black_king_moved, black_krook_moved, black_qrook_moved
        global legal_moves_cache
        row, file = Utils.button_to_rowfile(check_piece)
        destrow, destfile = Utils.button_to_rowfile(dest)
        if (destrow == 7 and white_to_move or destrow == 0 and not white_to_move) and issubclass(type(piecesLayout[row][file]), (w.Pawn, b.Pawn)):
            # Show the promotion GUI
            promoteUI = ChessPromotionUI()
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
                movenum+=1
                Frontend.update_move_list(movee,dest)

                # Just to test
                Backend.get_all_legal_moves(white_to_move)
                #Thread(target= lambda check=check: Calculations.minimax(depth=4, alpha=-math.inf, beta=math.inf, max_player=True if white_to_move else False, max_color=WHITE, check=check, begin_d=4)).start()
                return 200
            else:
                return 404
    
    def test_bot_callback(result):
        print(result)
    
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
    
    def move_other_format(move, row, file, piece_type):
        file_letters={0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        piece_types={w.Rook:'R', w.Knight:'N', w.Bishop:'B',w.Queen:'Q', w.King:'K', w.Pawn:'', b.Rook:'R', b.Knight:'N', b.Bishop:'B', b.Queen:'Q', b.King:'K', b.Pawn:''}
        promote=''
        first, last = '', ''
        if move[-1]=='c' and piece_types[piece_type]=='': 
            _, sfile=Utils.index_to_rowfile(int(move[0:2]))
            first=file_letters[sfile]
        else:
            first=piece_types[piece_type]
        if mate:
            last = '#'
        elif check and not mate:
            last = '+'
        elif move[-1]=='a':
            promote='=Q'
        elif move[-1]=='s':
            promote='=R'
        elif move[-1]=='d':
            promote='=B'
        elif move[-1]=='f':
            promote='=N'
        newformat=f"{first}{'x' if move[-1]=='c' else ''}{file_letters[file]}{row+1}{promote}{last}"
        return newformat

    def update_move_list(move, piece):
        global movenum, list_items, moves_list
        row,file=Utils.button_to_rowfile(piece)
        piece_type=type(piecesLayout[row][file])
        newformat = Frontend.move_other_format(move, row, file, piece_type)
        moves_list.append(move)
        if movenum%2==1:
            li=OneLineListItem(text=f"{math.ceil(movenum/2)}. {newformat}")
            move_list.add_widget(widget=li)
            list_items.append(li)
        else:
            list_items[int(movenum/2-1)].text+=f' {newformat}'
        
class Backend():
    # NOTE: Legal move format
    #   2 chars    2 chars  1 char
    # <index from><index to><type>
    # Types:
    # 'n' - normal
    # 'c' - capture
    # 'e' - en passant
    # 'k' or 'q' - King- or Queenside castling
    # 'a' promote queen
    # 's' promote rook
    # 'd' promote bishop
    # 'f' promote knight
    # Don't pay much attention to the flags for promotion
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
                    # Check if the pawn can promote
                    if (colorstr == 'w' and row == 7) or (colorstr == 'b' and row == 0):
                        # Pawn can promote
                        for protype in ['a', 's', 'd', 'f']:
                            legalmoves.append([pieceType.movement[1][0], protype])
                    legalmoves.append([pieceType.movement[1][0], 'n'])
            except:
                pass
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
                    if (piecesLayout[tmpRow][tmpFile] == None):
                        legalmoves.append([tmpmove, 'n'])
                    if (colorstr == 'b' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)))\
                    or (colorstr == 'w' and issubclass(type(piecesLayout[tmpRow][tmpFile]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen))):
                        legalmoves.append([tmpmove, 'c'])
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
        
        # Loop through every move and check if the king is in check when the move is made
        # If so, the piece is pinned or in the case of the king he'll wank into a check
        if legalmoves and not check_check:
            legalmovescopy = deepcopy(legalmoves)
            for move in legalmoves:
                mrow, mfile = Utils.index_to_rowfile(int(move[2:4]))
                tmpPiecesLayout = deepcopy(piecesLayout)
                piecesLayout[row][file] = None
                piecesLayout[mrow][mfile] = pieceType
                tstcheck = False
                if issubclass(type(pieceType), (w.King, b.King)):
                    tstcheck = Backend.check_check(int(move[2:4]), white_to_move)
                else:
                    tstcheck = Backend.check_check(white_king_index if white_to_move else black_king_index, white_to_move)
                if issubclass(type(pieceType), (w.King, b.King)):
                    print(move, Frontend.move_other_format(move, mrow, mfile, type(pieceType)), tstcheck)
                piecesLayout = deepcopy(tmpPiecesLayout)
                if tstcheck:
                    legalmovescopy.remove(move)
            legalmoves = deepcopy(legalmovescopy)
        return legalmoves
    
    def get_all_legal_moves(white:bool, check_check=False):
        '''
        ### This function generates the legal moves in the current position
        #### Each legal move is in the following format:
        ##### index from: 6 bits, index to: 6 bits, flag: 4 bits
        ##### ex. 0b0011000111000001 would be the move e2-e4 with the normal flagS
        '''
        legal_moves = np.zeros(shape=218, dtype=np.int32)
        counter = 0
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        multiplier = 1 if white else -1
        color_total_bitboard = black_total_bitboard if white else white_total_bitboard
        total_bitboard = white_total_bitboard | black_total_bitboard
        for piece in (white_pieces if white else black_pieces):
            index = int(piece.text)-1
            row, file = Utils.button_to_rowfile(piece)
            pieceClass:w.Pawn = piecesLayout[row][file] # The :w.Pawn is purely to get autocomplete
            if issubclass(type(pieceClass), (w.Pawn, b.Pawn)):
                # En passant
                if len(moves_list) > 0:
                    lastmove = moves_list[-1]
                    lmfrom, lmto = int(lastmove[0:2]), int(lastmove[2:4]) # lm is an abbreviation for last move
                    lmtorow, lmtofile = Utils.index_to_rowfile(lmto)
                    lmpieceType = piecesLayout[lmtorow][lmtofile]
                    if Backend.check_index_overlap(black_pawn_bitboard if white else white_pawn_bitboard, index+1) and file < 7 and abs(lmfrom - lmto) == 16 and issubclass(lmpieceType, (w.Pawn, b.Pawn)):
                        ofile, orow = pieceClass.movement[2][0]
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['e'])
                        counter += 1
                    elif Backend.check_index_overlap(black_pawn_bitboard if white else white_pawn_bitboard, index-1) and file > 0 and abs(lmfrom - lmto) == 16 and issubclass(lmpieceType, (w.Pawn, b.Pawn)):
                        ofile, orow = pieceClass.movement[3][0]
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['e'])
                        counter += 1
                # Capture
                if Backend.check_index_overlap(color_total_bitboard, index+(9 if white else -7)) and file < 7:
                    ofile, orow = pieceClass.movement[2][0]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['c'])
                    counter += 1
                elif Backend.check_index_overlap(color_total_bitboard, index+(7 if white else -9)) and file > 0:
                    ofile, orow = pieceClass.movement[3][0]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['c'])
                    counter += 1
                # Normal move
                print(index+8*multiplier, Backend.check_index_overlap(total_bitboard, index+8*multiplier))
                if not Backend.check_index_overlap(total_bitboard, index+8*multiplier):
                    ofile, orow = pieceClass.movement[1][0]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['n'])
                    counter += 1
                    # First move
                    if not Backend.check_index_overlap(total_bitboard, index+16*multiplier) and row == (1 if white else 6):
                        ofile, orow = pieceClass.movement[0][0]
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['n'])
                        counter += 1
            elif issubclass(type(pieceClass), (w.King, b.King)):
                white_king = isinstance(pieceClass, w.King)
                # Castle kingside
                if ((white_king and not white_king_moved and not white_krook_moved) or (not white_king and not black_king_moved and not black_krook_moved))\
                and not Backend.check_index_overlap(total_bitboard, index+1) and not Backend.check_index_overlap(total_bitboard, index+2):
                    ofile, orow = pieceClass.movement[1][0]
                    oofile, oorow = pieceClass.movement[1][1]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['k'])
                    legal_moves[counter+1] = Backend.move_to_int(row, file, row+oorow, file+oofile, legal_moves_flags['k'])
                    counter += 2
                # Castle queenside
                if ((white_king and not white_king_moved and not white_qrook_moved) or (not white_king and not black_king_moved and not black_qrook_moved))\
                and not Backend.check_index_overlap(total_bitboard, index-1) and not Backend.check_index_overlap(total_bitboard, index-2) and not Backend.check_index_overlap(total_bitboard, index-3):
                    ofile, orow = pieceClass.movement[0][0]
                    oofile, oorow = pieceClass.movement[0][1]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['q'])
                    legal_moves[counter+1] = Backend.move_to_int(row, file, row+oorow, file+oofile, legal_moves_flags['q'])
                    counter += 2
                # The rest of the moves
                for i in range(2, 10):
                    f, r = pieceClass.movement[i][0]
                    fto, rto = file+f, row+r
                    if fto > 7 or fto < 0 or rto > 7 or rto < 0:
                        continue
                    if Backend.check_index_overlap(color_total_bitboard, index+(8*r+f)):
                        legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['c'])
                        counter += 1
                    elif not Backend.check_index_overlap(total_bitboard, index+(8*r+f)):
                        legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['n'])
                        counter += 1
            else:
                for direction in pieceClass.movement:
                    for option in direction:
                        f, r = option
                        fto, rto = file+f, row+r
                        if fto > 7 or fto < 0 or rto > 7 or rto < 0:
                            break
                        if not Backend.check_index_overlap(total_bitboard, index+(8*r+f)):
                            legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['n'])
                            counter += 1
                        elif Backend.check_index_overlap(color_total_bitboard, index+(8*r+f)):
                            legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['c'])
                            counter += 1
                            break
                        else:
                            break
            if check_check:
                continue
            # Uhmm, I might need an attacking bitboard to do this properly
            # Future Patirck, that's your problem

        print(legal_moves)
        if counter == 0:
            return
        legal_moves = np.resize(legal_moves, counter)
        testee = []
        for m in legal_moves:
            m = m.item()
            print(m.bit_length())
            # TODO: MAKE THIS WAY MORE EFFICIENT
            movestr = f'{m:016b}'
            index_from = int(movestr[0:6], 2)
            index_to = int(movestr[6:12], 2)
            flag = list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(movestr[12:], 2))]
            testee.append(f'{index_from}{index_to}{flag}')
        print(testee)
        print(legal_moves)
        return legal_moves
    
    # Checks if the index given is 1 in the given bitboard
    def check_index_overlap(board:int, index:int) -> bool:
        '''
        Checks if the given index is 1 in the given bitboard.
        It shifts the board over by the index and performs a bitwise AND operation on the result and 1
        '''
        return board >> index & 1 == 1
    
    def move_to_int(row:int, file:int, rto:int, fto:int, flag:int) -> int:
        return int(f'0b{8*row+file:06b}{8*rto+fto:06b}{flag:04b}', 2)
    
    def format_legal_moves(legalmoves:list, row:int, file:int):
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

    def update_bitboards():
        global white_bishop_bitboard, white_king_bitboard, white_knight_bitboard, white_pawn_bitboard, white_queen_bitboard, white_rook_bitboard, black_bishop_bitboard, black_king_bitboard, black_knight_bitboard, black_pawn_bitboard, black_queen_bitboard, black_rook_bitboard
        global white_total_bitboard, black_total_bitboard
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
        white_total_bitboard = white_bishop_bitboard | white_king_bitboard | white_knight_bitboard | white_rook_bitboard | white_queen_bitboard | white_pawn_bitboard
        black_total_bitboard = black_bishop_bitboard | black_king_bitboard | black_knight_bitboard | black_rook_bitboard | black_queen_bitboard | black_pawn_bitboard
    
    def attacking_borboard():
        global attacking_bitboard

    def pin_bitboard():
        global pin_bitboard
        
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

    def pretty_print_position():
        pieces_unicode={
            w.King: '♚',
            w.Knight: '♞',
            w.Pawn: '♟',
            w.Queen: '♛',
            w.Rook: '♜',
            w.Bishop: '♝',
            b.King: '♔',
            b.Knight: '♘',
            b.Pawn: '♙',
            b.Queen: '♕',
            b.Rook: '♖',
            b.Bishop: '♗'
        }
        pretty = '-------------------------\n'
        for row in piecesLayout:
            for square in row:
                if square:
                    pretty += f'|{pieces_unicode[type(square)]} '
                else:
                    pretty += '|  '
            pretty += '|\n-------------------------\n'
        print(pretty, end='\r')