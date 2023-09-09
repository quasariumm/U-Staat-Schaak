import math
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button

from app import board_prim, board, piecesLayout

selected : Button = None
tempBackground_color = []

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        if selected == None and piecesLayout[math.floor(int(button.text)-1)][int(button.text)%8] != None:
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]
        elif piecesLayout[math.floor(int(button.text)-1)][int(button.text)%8] == None and selected == None:
            pass
        elif selected.text == button.text or piecesLayout[math.floor(int(button.text)-1)][int(button.text)%8] == None:
            selected.background_color = tempBackground_color
            selected = None
        else:
            selected.background_color = tempBackground_color
            selected = board[int(button.text)-1]
            tempBackground_color = selected.background_color
            r,g,b,a = selected.background_color
            selected.background_color = [r*0.5, g, b, a] if selected.background_color == get_color_from_hex(board_prim) else [r*0.75, g, b, a]

class Backend():
    def legal_moves(piece):
        pass