from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
import os, math, time

board_prim = "#795C34"
board_sec = "#E4D9CA"

board = []

class MainScreen(MDScreen):
    pass

class ChessBoard(MDGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = 8
        self.cols = 8
        self.orientation = 'lr-bt'
        for i in range(1,65):
            row = math.floor(i/8) + 1
            square = Button(
                background_color = 
                    get_color_from_hex(board_prim) 
                    if (i%2==0 if row%2==0 else i%2==1) else 
                    get_color_from_hex(board_sec),
                background_down = '',
                background_normal = '' # Attribute in which the piece image is inserted
            )
            board.append(square)
            self.add_widget(square, index=i-1)
        print(len(self.children))

class ChessApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boardState = []

    def build(self):
        self.theme_cls.theme_style = 'Dark'

        return Builder.load_file(os.path.dirname(__file__) + '\\app.kv')
        

if __name__ == "__main__":
    app = ChessApp()
    app.run()


# move_register is vakje rechtsboven dat zetten bijhoudt. 
# move_register = ChessBoardSquare(text="Zetten",background_color = color, color = [1,1,0,0],position = 305,240,size=15,240) # TI-84 (GR) scherm is 320x240 pixels.
# self.add_widget(move_register)
