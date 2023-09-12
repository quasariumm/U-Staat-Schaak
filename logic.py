import math,os
from pieces import White as w
from pieces import Black as b
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button

from app import board_prim, board, piecesLayout

selected : Button = None
tempBackground_color = []

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        row = math.floor((int(button.text)-1)/8)
        file = (int(button.text)-1)%8

        if selected != None :
            if selected != button: 
                Frontend.move(button)

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
        # moves = Backend.legal_moves(piece)
        # move_from = f'0{selected.text}' if int(selected.text)<10 else selected.text
        # move_to = f'0{piece.text}' if int(piece.text)<10 else piece.text
        # move = move_from +move_to
        # if move in moves: 
        piece.image.source = selected.image.source 
        selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        selected.background_color = tempBackground_color
        selected = None

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
            'bq': b.Queen()}
        for i,square in enumerate(board):
            piece = dictt[square.image.source[-7:-6]]
            row = math.floor((int(i.text)-1)/8)
            file = (int(i.text)-1)%8
            piecesLayout[row][file]= piece

