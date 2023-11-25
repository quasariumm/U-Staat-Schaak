from kivymd.app import MDApp
from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.graphics import *
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout, GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.popup import Popup
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivy.uix.button import Button
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import MDScrollView
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.core.window import Window
import os, math, time
from threading import Thread
import json
from copy import deepcopy

from pieces import White as w
from pieces import Black as b

import logic
import global_vars as gl
from bot import Calculations

Config.set('input', 'mouse', 'mouse,disable_multitouch')

board = [None] * 64
time_control = 600
increment = 0

app:MDApp = None
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gl.theme_elements['MainScreen'] = self

class ChessBoard(MDGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gl.theme_elements['ChessBoard'] = self
        self.rows = 8
        self.cols = 8
        self.orientation = 'lr-bt'
        for i in range(1,65):
            row = math.floor((i-1)/8) + 1
            color = get_color_from_hex(gl.user_color_theme['board_prim']) if (i%2==0 if row%2==0 else i%2==1) else get_color_from_hex(gl.user_color_theme['board_sec'])
            cbs = ChessBoardSquare(text=str(i),background_color = color, color = [1,1,1,0])
            self.add_widget(cbs)
        
        for el in self.children:
            board[int(el.text)-1] = el
        self.update_board()
    
    def update_board(self):
        for i,row in enumerate(piecesLayout):
            for j,piece in enumerate(row):
                if piece:
                    board[8*i+j].image.source = piece.imgPath.format(gl.user_piece_set)
                else:
                    board[8*i+j].image.source = os.path.dirname(__file__) + '\\data\\img\\empty.png'
    
    def turn_board(self) -> None:
        self.orientation = 'rl-tb' if self.orientation == 'lr-bt' else 'lr-bt'
        gl.theme_elements['MainScreen'].clocks_switched = 0 if gl.theme_elements['MainScreen'].clocks_switched == 1 else 1

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
                    el.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\{gl.user_piece_set}\\w{el.text}n.png"
        else:
            for el in self.children:
                if isinstance(el, Button):
                    el.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\{gl.user_piece_set}\\b{el.text}n.png"
    
    def cancel(*args):
        logic.promotionStatus = 2
        logic.promotionEvent.set()

class MovesList(MDList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logic.move_list = self
        gl.theme_elements['MovesList'] = self
        gl.move_list_scrollview = self.parent

class TopClock(MDFillRoundFlatIconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global app
        logic.topClock = self
        gl.theme_elements['TopClock'] = self
        ChessApp.init_clocks(app)

class BottomClock(MDFillRoundFlatIconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global app
        logic.bottomClock = self
        gl.theme_elements['BottomClock'] = self
        ChessApp.init_clocks(app)

class SettingsMenu(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_themes = list(gl.themes['color_themes'].keys())
        menu_items_color = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{ct}",
                "text_color":[1,1,1,1],
                "height": dp(48),
                "ver_growth":"down",
                "on_release": lambda x=f"{ct}": self.set_item(self.menu_color, self.di_color, x),
            } for ct in self.color_themes
        ]
        self.di_color.text = gl.themes['user_save']['color_theme']
        self.menu_color = MDDropdownMenu(caller=self.di_color, items=menu_items_color, position='bottom', width_mult=4, background_color=get_color_from_hex('#121212'))
        self.piece_sets = gl.themes['piece_sets']
        menu_items_pieces = [
            {
                "viewclass":"OneLineListItem",
                "text": f"{ps}",
                "text_color":[1,1,1,1],
                "height": dp(48),
                "ver_growth":"down",
                "on_release": lambda x=f"{ps}": self.set_item(self.menu_pieces, self.di_pieces, x),
            } for ps in self.piece_sets
        ]
        self.di_pieces.text = gl.themes['user_save']['piece_set']
        self.menu_pieces = MDDropdownMenu(caller=self.di_pieces, items=menu_items_pieces, position='bottom', width_mult=4, background_color=get_color_from_hex('#121212'))
        self.menu_color.max_height = dp(4 * 48)
        self.menu_pieces.max_height = dp(4 * 48)
        self.menu_color.bind()
        self.menu_pieces.bind()
    
    def set_item(self, menu:MDDropdownMenu, item:MDDropDownItem, value:str) -> None:
        item.set_item(value)
        menu.dismiss()
        user_ct = value if menu == self.menu_color else gl.themes['user_save']['color_theme']
        user_ps = value if menu == self.menu_pieces else gl.themes['user_save']['piece_set']
        gl.themes['user_save'] = {'color_theme':user_ct, 'piece_set':user_ps}
        gl.user_color_theme = deepcopy(gl.themes['color_themes'][gl.themes['user_save']['color_theme']])
        gl.user_piece_set = deepcopy(gl.themes['user_save']['piece_set'])
        update_theming()
        update_theme_user_save(
            theme_name=user_ct,
            piece_set=user_ps
        )
    
    def on_dismiss(*args) -> None:
        gl.settings_menu = None
    
class MainMenuOptions(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (0.9, 0.925)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.mode_choice = 'No bot'
        self.board_switch = False
        modeList = [
            {
                "viewclass": "OneLineListItem",
                "text": m,
                "height": dp(56),
                "ver_growth":"down",
                "on_release": lambda x=m: self.set_item(x)
            } for m in ['No bot', 'Bot as white', 'Bot as black', 'Bot vs bot']
        ]
        self.menu_mode = MDDropdownMenu(caller=self.mode, items = modeList, position='bottom', width_mult=4)
        self.menu_mode.bind()

    def set_item(self, value:str) -> None:
        self.mode.set_item(value)
        self.mode_choice = value
        self.menu_mode.dismiss()
    
    def start_game(self) -> None:
        logic.bot_on = self.mode_choice != 'No bot'
        match self.mode_choice:
            case 'Bot as white':
                logic.bot_color = 1
            case 'Bot as black':
                logic.bot_color = -1
            case 'Bot vs bot':
                logic.bot_color = 2
        logic.board_turns = self.main.turn_layout.turn.active
        logic.time_control = 60*int(self.main.time.min.text)+int(self.main.time.sec.text)
        logic.increment = int(self.main.time.inc.text)
        custom_fen = self.main.custom_fen.text
        e = None
        if custom_fen != '':
            e = logic.Backend.load_fen(custom_fen)
        else:
            e = logic.Backend.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        if e:
            for el in gl.theme_elements['MainScreen'].bl.obl.move_list.children:
                if type(el) != MDLabel:
                    gl.theme_elements['MainScreen'].bl.obl.move_list.remove_widget(el)
            logic.Frontend.reset_game()
            return
        logic.started = True
        logic.Frontend.switch_movelist_mainmenu()
        # Set both clocks to the current time control
        mins, secs = math.ceil((logic.time_control+1)/60)-1, math.ceil(logic.time_control)%60
        gl.theme_elements['BottomClock'].text = '{:02d}:{:02d}'.format(mins,secs)
        gl.theme_elements['TopClock'].text = '{:02d}:{:02d}'.format(mins,secs)
        # Give bots unlimited time
        match logic.bot_color:
            case 1: # White
                gl.theme_elements['BottomClock'].text = '--:--'
            case -1: # Black
                gl.theme_elements['TopClock'].text = '--:--'
            case 2: # Bot vs bot
                gl.theme_elements['BottomClock'].text = '--:--'
                gl.theme_elements['TopClock'].text = '--:--'
        if logic.bot_on and logic.bot_color == 1:
            gl.theme_elements['ChessBoard'].turn_board()
            Thread(target=Calculations.minimax, kwargs={'depth': 4, 'alpha':-math.inf, 'beta':math.inf, 'max_player':logic.white_to_move, 'max_color':1, 'check':logic.check, 'begin_d':4}).start()
        elif logic.bot_on and logic.bot_color == 2:
            Thread(target=Calculations.minimax, kwargs={'depth': 4, 'alpha':-math.inf, 'beta':math.inf, 'max_player':logic.white_to_move, 'max_color':1, 'check':logic.check, 'begin_d':4}).start()
        else:
            logic.b_clock.toggle()

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
    
    def top_bar_callback(self, option):
        print(option)
        if option == 'settings' and gl.settings_menu:
            gl.settings_menu.parent.dismiss()
        elif option == 'settings' and not gl.settings_menu:
            sm = SettingsMenu()
            gl.settings_menu = sm
            popup = Popup(title='Settings', content=sm, size_hint=(0.5,0.3))
            popup.open()
            popup.bind(on_dismiss=SettingsMenu.on_dismiss)
        elif option == 'end_game' and logic.started:
            logic.Frontend.reset_game()
    
    def on_stop(self):
        if logic.t_clock and logic.b_clock:
            if logic.t_clock.started:
                logic.t_clock.toggle()
            if logic.b_clock.started:
                logic.b_clock.toggle()

    def on_start(self):
        logic.Backend.update_bitboards(True)
        lm = logic.Backend.get_all_legal_moves(True)
        logic.Backend.legal_moves_per_square(lm)
        update_theming()
        for el in gl.theme_elements['MainScreen'].bl.obl.move_list.children:
            if type(el) == MDScrollView:
                gl.theme_elements['MainScreen'].bl.obl.move_list.remove_widget(el)
        mo = MainMenuOptions()
        gl.theme_elements['MainScreen'].bl.obl.move_list.add_widget(mo)
        return super().on_start()

    def build(self):
        with open(os.path.dirname(__file__) + '\\themes.json', 'r') as f:
            ctx = json.load(f)
            f.close()
        gl.themes = deepcopy(ctx)
        gl.user_color_theme = deepcopy(gl.themes['color_themes'][gl.themes['user_save']['color_theme']])
        gl.user_piece_set = deepcopy(gl.themes['user_save']['piece_set'])
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = 'M2'
        Window.bind(on_request_close=self.exit_promotion)
        return Builder.load_file(os.path.dirname(__file__) + '\\app.kv')

def update_theming():
    if gl.themes['user_save']['color_theme'].find('Light') > -1:
        app.theme_cls.theme_style = 'Light'
        # Fix text color
        gl.theme_elements['MainScreen'].bl.obl.move_list.la.text_color = [0,0,0,1]
    else:
        app.theme_cls.theme_style = 'Dark'
        # Fix text color
        gl.theme_elements['MainScreen'].bl.obl.move_list.la.text_color = [1,1,1,1]
    # Main screen background
    gl.theme_elements['MainScreen'].backgr_color = get_color_from_hex(gl.user_color_theme['background_color'])
    # Chess board
    for i,el in enumerate(gl.theme_elements['ChessBoard'].children):
        row = math.floor(i/8) + 1
        color = get_color_from_hex(gl.user_color_theme['board_prim']) if ((i+1)%2==0 if row%2==0 else (i+1)%2==1) else get_color_from_hex(gl.user_color_theme['board_sec'])
        el.background_color = color
    # Piece set
    gl.theme_elements['ChessBoard'].update_board()
    # Clocks
    gl.theme_elements['TopClock'].background_color = get_color_from_hex(gl.user_color_theme['clock_color_black'])
    gl.theme_elements['TopClock'].disabled_color = get_color_from_hex(gl.user_color_theme['clock_color_black'])
    gl.theme_elements['BottomClock'].background_color = get_color_from_hex(gl.user_color_theme['clock_color_white'])
    gl.theme_elements['BottomClock'].disabled_color = get_color_from_hex(gl.user_color_theme['clock_color_white'])
    # Moves list
    gl.theme_elements['MainScreen'].move_list_backgr_color = get_color_from_hex(gl.user_color_theme['move_list_color'])
    if logic.list_items:
        for olli in logic.list_items:
            olli.text_color = app.theme_cls.text_color
    # Top bar
    gl.theme_elements['MainScreen'].bl.topbar.md_bg_color = gl.user_color_theme['top_bar_color']

def update_theme_user_save(theme_name:str = None, piece_set:str = None) -> None:
    gl.themes['user_save'] = {'color_theme':theme_name, 'piece_set':piece_set}
    with open(os.path.dirname(__file__) + '\\themes.json', 'w') as f:
        f.write(json.dumps(gl.themes, indent=4))

if __name__ == "__main__":
    app = ChessApp()
    app.run()