from kivymd.uix.boxlayout import MDBoxLayout

themes:dict = {}
user_color_theme:dict = {}
user_piece_set:str = ''
theme_elements = {
    'MainScreen':None,
    'ChessBoard':None,
    'TopClock':None,
    'BottomClock':None,
    'MovesList':None
}
settings_menu:MDBoxLayout = None
move_list_scrollview = None

data_path = None