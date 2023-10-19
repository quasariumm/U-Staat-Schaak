from kivymd.app import MDApp
from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.graphics import *
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout, GridLayout
from kivy.uix.button import Button
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import os, math, time
from threading import Thread

from pieces import White as w
from pieces import Black as b

import logic

Config.set('input', 'mouse', 'mouse,disable_multitouch')

board_prim = "#795C34"
board_sec = "#E4D9CA"
board = [None] * 64
time_control = 600

app = None
#                                                        .::.
#                                             _()_       _::_
#                                   _O      _/____\_   _/____\_
#            _  _  _     ^^__      / //\    \      /   \      /
#           | || || |   /  - \_   {     }    \____/     \____/
#           |_______| <|    __<    \___/     (____)     (____)
#     _     \__ ___ / <|    \      (___)      |  |       |  |
#    (_)     |___|_|  <|     \      |_|       |__|       |__|
#   (___)    |_|___|  <|______\    /   \     /    \     /    \
#   _|_|_    |___|_|   _|____|_   (_____)   (______)   (______)
#  (_____)  (_______) (________) (_______) (________) (________)
#  /_____\  /_______\ /________\ /_______\ /________\ /________\
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
        self.update_board()
    
    def update_board(self):
        for i,row in enumerate(piecesLayout):
            for j,piece in enumerate(row):
                if piece:
                    board[8*i+j].image.source = piece.imgPath
                else:
                    board[8*i+j].image.source = os.path.dirname(__file__) + '\\data\\img\\empty.png'

class ChessBoardSquare(Button):
    def pressAction(button):
        logic.Frontend.square_press_action(button)

class ChessPromotionPiece(Button):
    def pressAction(button):
        logic.promotionStatus = 1
        logic.promotionEvent.set()
        logic.promotionType = button.text

class ChessPromotionUI(GridLayout):
    def change_color(self, pieceType):
        if issubclass(type(pieceType), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)):
            for el in self.children:
                if isinstance(el, Button):
                    el.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\Default\\w{el.text}n.png"
        else:
            for el in self.children:
                if isinstance(el, Button):
                    el.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\Default\\b{el.text}n.png"
    
    def cancel(*args):
        logic.promotionStatus = 2
        logic.promotionEvent.set()

class MovesList(MDList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logic.move_list = self

class TopClock(MDFillRoundFlatIconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global app
        logic.topClock = self
        ChessApp.init_clocks(app)

class BottomClock(MDFillRoundFlatIconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global app
        logic.bottomClock = self
        ChessApp.init_clocks(app)

class ChessApp(MDApp):
    def exit_promotion(*args):
        logic.promotionStatus = 2
        logic.promotionEvent.set()

    def init_clocks(self):
        global time_control
        if (logic.topClock is None) or (logic.bottomClock is None):
            return
        logic.topClock.text = '{:02d}:{:02d}'.format(math.floor(time_control/60), time_control%60)
        logic.bottomClock.text = '{:02d}:{:02d}'.format(math.floor(time_control/60), time_control%60)
        logic.t_clock = logic.Clock(clock=logic.topClock)
        logic.b_clock = logic.Clock(clock=logic.bottomClock)
        logic.b_clock.toggle(t=time_control)
    
    def on_stop(self):
        if logic.t_clock and logic.b_clock:
            if logic.t_clock.started:
                logic.t_clock.toggle()
            if logic.b_clock.started:
                logic.b_clock.toggle()

    def on_start(self):
        logic.Tests.legal_move_time_comparison()
        return super().on_start()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        Window.bind(on_request_close=self.exit_promotion)
        return Builder.load_file(os.path.dirname(__file__) + '\\app.kv')        

if __name__ == "__main__":
    app = ChessApp()
    app.run()