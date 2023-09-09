from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.graphics import *
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.button import Button
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.utils import get_color_from_hex
import os, math, time

from pieces import White as w
from pieces import Black as b

import logic

board_prim = "#795C34"
board_sec = "#E4D9CA"

board = [None] * 64

# PiecesLayout format: [a1, a2, ..., h7, h8]
piecesLayout = [
    [w.Rook(), w.Knight(), w.Bishop(), w.Queen(), w.King(), w.Bishop(), w.Knight(), w.Rook()],
    [w.Pawn(), w.Pawn(), w.Pawn(), w.Pawn(), w.Pawn(), w.Pawn(), w.Pawn(), w.Pawn()],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None], 
    [None, None, None, None, None, None, None, None],
    [b.Pawn(), b.Pawn(), b.Pawn(), b.Pawn(), b.Pawn(), b.Pawn(), b.Pawn(), b.Pawn()],
    [b.Rook(), b.Knight(), b.Bishop(), b.Queen(), b.King(), b.Bishop(), b.Knight(), b.Rook()]
]

class MainScreen(MDScreen):
    pass

class ChessBoard(MDGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = 8
        self.cols = 8
        self.orientation = 'lr-bt'
        for i in range(1,65):
            row = math.floor((i-1)/8) + 1
            color = get_color_from_hex(board_prim) if (i%2==0 if row%2==0 else i%2==1) else get_color_from_hex(board_sec)
            cbs = ChessBoardSquare(text=str(i),background_color = color, color = [1,1,1,0])
            self.add_widget(cbs)
        
        for el in self.children:
            board[int(el.text)-1] = el
    
    def update_board(self):
        for i,row in enumerate(piecesLayout):
            for i,piece in enumerate(row):
                if piece:
                    board[i].image.source = piece.imgPath
                else:
                    board[i].image.source = os.path.dirname(__file__) + '\\data\\img\\empty.png'

class ChessBoardSquare(Button):
    def pressAction(button):
        logic.Frontend.square_press_action(button)

class MovesList(MDList):
    pass

class ChessApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boardState = []

    def build(self):
        self.theme_cls.theme_style = 'Dark'

        return Builder.load_file(os.path.dirname(__file__) + '\\app.kv')

    def on_start(self):
        ChessBoard.update_board(ChessBoard)
        print(ChessBoard.width)
        return super().on_start()
        

if __name__ == "__main__":
    app = ChessApp()
    app.run()
