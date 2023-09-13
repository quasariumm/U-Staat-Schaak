import math,os
from pieces import White as w
from pieces import Black as b
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button

from app import board_prim, board, piecesLayout

selected : Button = None
tempBackground_color = []
white_to_move = True

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        global white_to_move
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8

        if selected != None :
            if selected != button: 
                print(selected.image.source[-7])
                if (selected.image.source[-7] == 'w' and white_to_move) or (selected.image.source[-7] == 'b' and not white_to_move):
                    Frontend.move(button)
                    return
    	    
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
        
    def move(piece: Button):
        global selected
        global tempBackground_color
        global white_to_move
        # moves = Backend.legal_moves(piece)
        # move_from = f'0{selected.text}' if int(selected.text)<10 else selected.text
        # move_to = f'0{piece.text}' if int(piece.text)<10 else piece.text
        # move = move_from +move_to
        # if move in moves: 
        piece.image.source = selected.image.source 
        selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        selected.background_color = tempBackground_color
        selected = None
        white_to_move = not white_to_move
        Backend.update_pieces_layout()

class Backend():
    def legal_moves(piece):
        pass
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

