import math,os
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button

from app import board_prim, board, piecesLayout
from pieces import White as w
from pieces import Black as b

selected : Button = None
tempBackground_color = []

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
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8

        # NOTE: TEST
        Frontend.clear_legal_moves_indicators()
        if piecesLayout[row][file] != None:
            Backend.legal_moves(button)

        if selected == None and piecesLayout[row][file] != None:
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]
        elif piecesLayout[row][file] == None and selected == None:
            pass
        elif selected.text == button.text or piecesLayout[row][file] == None:
            selected.background_color = tempBackground_color
            selected = None
        else:
            selected.background_color = tempBackground_color
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]

    def clear_legal_moves_indicators():
        for square in board:
            square.background_normal = ''
            square.background_down = ''

class Backend():
    def legal_moves(button):
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8
        pieceType = piecesLayout[row][file]
        if pieceType in [w.Pawn(), b.Pawn()]:
            pass
        elif pieceType in [w.King(), b.King()]:
            pass
        else:
            for direction in pieceType.movement:
                for option in direction:
                    tmpRow = row + option[1]
                    tmpFile = file + option[0]
                    if tmpRow > 7 or tmpRow < 0 or tmpFile > 7 or tmpFile < 0:
                        break
                    else:
                        board[8*tmpRow+tmpFile].background_normal = os.path.dirname(__file__) + '\\data\\img\\legal_capture.png'