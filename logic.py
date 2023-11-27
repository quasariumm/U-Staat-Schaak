import math,os,time
import numpy as np
from collections import Counter
from copy import deepcopy
from threading import Thread, Event
import multiprocessing as mp

from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivymd.uix.list import OneLineListItem
from kivy.uix.popup import Popup
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import mainthread

from app import board, piecesLayout, ChessPromotionUI, app, MainMenuOptions, MovesList
from app import time_control, increment
from pieces import White as w
from pieces import Black as b
from bot import Calculations, Misc, WHITE, BLACK

import global_vars as gl

movenum=0
move_list = []
list_items=[]

moves_fen = []
moves_posfen = []

selected : Button = None
tempBackground_color = []
white_to_move = True
t_clock, b_clock = None, None
topClock, bottomClock = None, None
legal_moves_per_square = {}

# Castling requirements
white_krook_moved = False
white_qrook_moved = False
white_king_moved = False
black_krook_moved = False
black_qrook_moved = False
black_king_moved = False

check = False
mate = False
repitition = 0
fiftymoverule = 0
white_king_index = 4
black_king_index = 60
en_passant_target_index = 0

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

piece_bitboards = [
    'white_king_bitboard', 'black_king_bitboard',
    'white_queen_bitboard', 'black_queen_bitboard',
    'white_bishop_bitboard', 'black_bishop_bitboard',
    'white_knight_bitboard', 'black_knight_bitboard',
    'white_rook_bitboard', 'black_rook_bitboard',
    'white_pawn_bitboard', 'black_pawn_bitboard'
]

bitboard_name_to_pieceClass = {
    'white_king_bitboard': w.King(),
    'white_queen_bitboard': w.Queen(),
    'white_bishop_bitboard': w.Bishop(),
    'white_knight_bitboard': w.Knight(),
    'white_rook_bitboard': w.Rook(),
    'white_pawn_bitboard': w.Pawn(),
    'black_king_bitboard': b.King(),
    'black_queen_bitboard': b.Queen(),
    'black_bishop_bitboard': b.Bishop(),
    'black_knight_bitboard': b.Knight(),
    'black_rook_bitboard': b.Rook(),
    'black_pawn_bitboard': b.Pawn()
}

attacking_bitboard = 0
king_attack_bitboard = 0
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
    'pn': 0b1001,
    'qq': 0b1010,
    'qr': 0b1011,
    'qb': 0b1100,
    'qn': 0b1101
}

moves_list = []
promotionStatus = 0
promotionType = ''
promotionEvent = Event()

bot_on = False
# NOTE: if bot_color is 2 it's a bot vs bot game
bot_color = WHITE
bot_move = False

board_turns = False
started = False

class Tests():
    pass

class Frontend():
    def square_press_action(button):
        global selected
        global tempBackground_color
        global white_to_move
        row, file = Utils.button_to_rowfile(button)
        if not started or bot_move:
            return

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
            selected.background_color = [r*0.5, g, bl, a] if selected.background_color == get_color_from_hex(gl.user_color_theme['board_prim']) else [r*0.75, g, bl, a]
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
            selected.background_color = [r*0.5, g, bl, a] if selected.background_color == get_color_from_hex(gl.user_color_theme['board_prim']) else [r*0.75, g, bl, a]
            if (issubclass(type(piecesLayout[row][file]), (w.Pawn, w.King, w.Knight, w.Bishop, w.Rook, w.Queen)) and white_to_move) or (issubclass(type(piecesLayout[row][file]), (b.Pawn, b.King, b.Knight, b.Bishop, b.Rook, b.Queen)) and not white_to_move):
                Frontend.show_legal_move_indicators(button)
        
    def move(check_piece:Button, dest: Button) -> int:
        global selected
        global tempBackground_color
        global white_to_move
        global check, mate, white_king_index, black_king_index
        global movenum
        global white_king_moved, white_krook_moved, white_qrook_moved, black_king_moved, black_krook_moved, black_qrook_moved
        global legal_moves_per_square, legal_moves_flags
        global t_clock,b_clock
        row, file = Utils.button_to_rowfile(check_piece)
        destrow, destfile = Utils.button_to_rowfile(dest)
        pieceClass = Utils.get_piece_type(8*row+file)()

        try:
            moves = legal_moves_per_square[int(selected.text)-1]
            moves_otherformat = [int(f'{m:016b}'[0:12], 2) for m in moves]
            move = int(f'{int(selected.text)-1:06b}{int(dest.text)-1:06b}', 2)
        except:
            return
        if moves:
            if move in moves_otherformat:
                if (destrow == (7 if white_to_move else 0)) and issubclass(type(piecesLayout[row][file]), (w.Pawn, b.Pawn)):
                    # Show the promotion GUI
                    promoteUI = ChessPromotionUI()
                    popup = Popup(title='Select piece type', content=promoteUI, size_hint=(0.25, 0.35))
                    promoteUI.change_color(piecesLayout[row][file])
                    popup.bind(on_dismiss=promoteUI.cancel)
                    popup.open()
                    Thread(target=Frontend.promotionMove, args=[check_piece, dest, popup]).start()
                    return 200
                movee = moves[moves_otherformat.index(move)]
                flag = list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(f'{movee:016b}'[12:], 2))]
                Frontend.doMove(dest, flag, row=row, file=file, pieceClass=pieceClass, check_piece=check_piece)
                white_to_move = not white_to_move
                # Check if rook or king has moved
                if isinstance(pieceClass, w.King):
                    white_king_index = int(dest.text)-1
                    if not white_king_moved:
                        white_king_moved = True
                elif isinstance(pieceClass, b.King):
                    black_king_index = int(dest.text)-1
                    if not black_king_moved:
                        black_king_moved = True
                elif isinstance(pieceClass, w.Rook):
                    if file == 0 and not white_qrook_moved:
                        white_qrook_moved = True
                    elif file == 7 and not white_krook_moved:
                        white_krook_moved = True
                elif isinstance(pieceClass, b.Rook):
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
                Frontend.move_rest(movee, pieceClass)
                return 200
            else:
                return 404
    
    @mainthread
    def move_rest(move:int, pieceClass) -> None:
        global movenum, check, mate
        global attacking_bitboard, white_king_index, black_king_index
        global bot_color, bot_on, white_to_move
        global moves_list
        global moves_fen, moves_posfen
        global bot_move
        global t_clock, b_clock
        Backend.update_pieces_layout()
        Backend.update_bitboards(white_to_move)
        check = Backend.check_index_overlap(attacking_bitboard, white_king_index if white_to_move else black_king_index)
        Frontend.clear_legal_moves_indicators()
        movenum+=1
        moves_list.append(move)
        lm = Backend.get_all_legal_moves(white_to_move)
        Backend.legal_moves_per_square(lm)
        # NOTE: The draw local variable gives the type of draw (Stalemate, 50-move rule, threefold repitition)
        mate, draw = Backend.mate_and_draw(move)
        fen = Utils.position_to_fen()[0]
        moves_fen.append(fen)
        moves_posfen.append(fen.split(' ', maxsplit=1)[0])
        if mate:
            Frontend.invoke_popup(f"{'Black' if white_to_move else 'White'} won by checkmate")
            Frontend.reset_game()
            return
        if draw != '':
            Frontend.invoke_popup(f"Draw by {draw}")
            Frontend.reset_game()
            return
        Frontend.update_move_list(move, pieceClass)

        if board_turns and not bot_on:
            gl.theme_elements['ChessBoard'].turn_board()
        time.sleep(0.2)
        if ((bot_color == BLACK and not white_to_move) or (bot_color == WHITE and white_to_move) or bot_color == 2) and bot_on:
            clock = None if bot_color == 2 else b_clock if bot_color == BLACK else t_clock
            if clock: clock.toggle()
            bot_move = True
            Thread(target=Calculations.minimax, kwargs={'depth': 4, 'alpha':-math.inf, 'beta':math.inf, 'max_player':white_to_move, 'max_color':WHITE, 'check':check, 'begin_d':4}).start()
        else:
            if (bot_on and bot_color not in [-1,2]) or not bot_on: t_clock.toggle()
            if (bot_on and bot_color not in [1,2]) or not bot_on: b_clock.toggle()

    def reset_game() -> None:
        global movenum, move_list, list_items, moves_fen, moves_posfen, selected
        global white_to_move, fiftymoverule, white_king_index, black_king_index
        global moves_list, started
        global t_clock, b_clock
        global check
        with open(os.path.dirname(__file__) + "\\data\\log\\latest.log", 'w') as f:
            f.write('\n'.join(moves_fen))
            f.close()
        movenum = 0; move_list = []; list_items = []; moves_fen = []; moves_posfen = []; selected = None
        white_to_move = True; fiftymoverule = 0; white_king_index = 4; black_king_index = 60; moves_list = []
        started = False; check = False
        if t_clock and b_clock:
            if t_clock.started:
                t_clock.toggle()
            if b_clock.started:
                b_clock.toggle()
        # Reset the clocks to 10:00
        gl.theme_elements['TopClock'].text = '10:00'
        gl.theme_elements['BottomClock'].text = '10:00'
        Frontend.switch_movelist_mainmenu()
        Backend.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    
    def test_bot_callback(result:tuple[int,float]):
        fi, _, _ = Utils.move_to_fi_ti_flag(result[0])
        piece_type = Utils.get_piece_type(fi)()
        new_format = Frontend.move_other_format(result[0], piece_type)
        print(new_format, result[1])
    
    def reset_event():
        global promotionStatus, promotionEvent
        promotionEvent.clear()
        promotionStatus = 0
    
    def promotionMove(check_piece, dest:Button, popup:Popup, bot_move:bool=False):
        global selected
        global tempBackground_color
        global white_to_move
        global check, mate, white_king_index, black_king_index
        global movenum
        global white_king_moved, white_krook_moved, white_qrook_moved, black_king_moved, black_krook_moved, black_qrook_moved
        global legal_moves_per_square, legal_moves_flags
        global promotionStatus, promotionEvent
        if not bot_move:
            promotionEvent.wait()
            if promotionStatus == 2:
                popup.dismiss()
                Frontend.reset_event()
                return 418
            popup.dismiss()
        Frontend.reset_event()
        row, file = Utils.button_to_rowfile(selected)
        check_pieceClass = Utils.get_piece_type(8*row+file)()
        try:
            moves = legal_moves_per_square[int(selected.text)-1]
            moves_otherformat = [int(f'{m:016b}'[0:12], 2) for m in moves]
            move = int(f'{int(selected.text)-1:06b}{int(dest.text)-1:06b}', 2)
        except:
            return
        if moves:
            if move in moves_otherformat:
                movee = moves[moves_otherformat.index(move)]
                Frontend.doMove(dest, list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(f'{movee:016b}'[12:], 2))])
                white_to_move = not white_to_move
                Frontend.move_rest(movee, check_pieceClass)
                return 200
        else:
            return 404
    
    @mainthread
    def doMove(dest:Button, flag:str, row:int=None, file:int=None, pieceClass=None, check_piece:Button=None) -> None:
        global selected
        if flag == 'e':
            toi = int(dest.text)-1
            pci = toi + (-8 if white_to_move else 8) # pci: Pawn Capture Index
            board[toi].image.source = check_piece.image.source
            check_piece.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
            board[pci].image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        elif flag == 'k':
            movement = pieceClass.movement[1][0]
            dest = board[8*(row+movement[1])+(file+movement[0])]
            dest.image.source = check_piece.image.source
            check_piece.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
            movement = pieceClass.movement[1][1]
            rook = board[8*(row+movement[1])+(file+movement[0])]
            board[8*(row)+(file+1)].image.source = rook.image.source
            rook.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        elif flag == 'q':
            movement = pieceClass.movement[0][0]
            dest = board[8*(row+movement[1])+(file+movement[0])]
            dest.image.source = check_piece.image.source
            check_piece.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
            movement = pieceClass.movement[0][1]
            rook = board[8*(row+movement[1])+(file+movement[0])]
            board[8*(row)+(file-1)].image.source = rook.image.source
            rook.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        elif len(flag) == 2:
            dest.image.source = os.path.dirname(__file__) + f"\\data\\img\\pieces\\{gl.user_piece_set}\\{'w' if not white_to_move else 'b'}{promotionType}n.png"
            selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        else:
            dest.image.source = selected.image.source 
            selected.image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
        selected.background_color = tempBackground_color
        selected = None

    def show_legal_move_indicators(button:Button) -> None:
        global legal_moves_per_square, legal_moves_flags
        try:
            moves = legal_moves_per_square[int(button.text)-1]
            if moves:
                for move in moves:
                    movestr = f'{move:016b}'
                    t_index = int(movestr[6:12], 2)
                    flag = 'capture' if list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(movestr[12:], 2))] in ['c', 'e', 'qq' ,'qr', 'qb', 'qn'] else 'normal'
                    board[t_index].background_normal = os.path.dirname(__file__) + f'\\data\\img\\legal_{flag}.png'
        except:
            return

    def clear_legal_moves_indicators():
        for square in board:
            square.background_normal = ''
            square.background_down = ''
    
    def move_other_format(move:int, pieceClass) -> str:
        file_letters={0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        piece_types={w.Rook:'R', w.Knight:'N', w.Bishop:'B',w.Queen:'Q', w.King:'K', w.Pawn:'', b.Rook:'R', b.Knight:'N', b.Bishop:'B', b.Queen:'Q', b.King:'K', b.Pawn:''}
        promote=''
        first, last = '', ''
        movestr = f'{move:016b}'
        s_index, t_index, flag = int(movestr[0:6], 2), int(movestr[6:12], 2), list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(movestr[12:], 2))]
        row, file = Utils.index_to_rowfile(t_index)
        if flag == 'k':
            return 'O-O'
        elif flag == 'q':
            return 'O-O-O'
        if flag in ['c', 'e', 'qq', 'qr', 'qb', 'qn'] and piece_types[type(pieceClass)]=='': 
            _, sfile=Utils.index_to_rowfile(s_index)
            first=file_letters[sfile]
        else:
            first=piece_types[type(pieceClass)]
        if mate:
            last = '#'
        elif check and not mate:
            last = '+'
        if flag in ['pq', 'qq']:
            promote='=Q'
        elif flag in ['pr', 'qr']:
            promote='=R'
        elif flag in ['pb', 'qb']:
            promote='=B'
        elif flag in ['pn', 'qn']:
            promote='=N'
        newformat=f"{first}{'x' if (flag in ['c', 'e'] or (flag[0] == 'q' and len(flag) == 2)) else ''}{file_letters[file]}{row+1}{promote}{last}"
        return newformat

    def update_move_list(move:int, pieceClass) -> None:
        global movenum, list_items
        newformat = Frontend.move_other_format(move, pieceClass)
        if movenum%2==1:
            li=OneLineListItem(text=f"{math.ceil(movenum/2)}. {newformat}")
            move_list.add_widget(widget=li)
            list_items.append(li)
        else:
            list_items[int(movenum/2-1)].text+=f' {newformat}'
    
    def invoke_popup(message:str) -> None:
        popup = Popup(title='Game over', content = MDLabel(text=message), size_hint=(0.25, 0.15), padding=[25,0,25,0])
        popup.open()
    
    def switch_movelist_mainmenu() -> None:
        if started:
            for el in gl.theme_elements['MainScreen'].bl.obl.move_list.children:
                if type(el) != MDLabel:
                    gl.theme_elements['MainScreen'].bl.obl.move_list.remove_widget(el)
            scroll_view = MDScrollView(size_hint_y=0.8,padding=[20,0,20,30])
            scroll_view.add_widget(MovesList())
            gl.theme_elements['MainScreen'].bl.obl.move_list.add_widget(scroll_view)
            gl.theme_elements['MainScreen'].bl.obl.move_list.la.text = 'Moves'
        else:
            for el in gl.theme_elements['MainScreen'].bl.obl.move_list.children:
                if type(el) == MDScrollView:
                    gl.theme_elements['MainScreen'].bl.obl.move_list.remove_widget(el)
            mmo = MainMenuOptions()
            gl.theme_elements['MainScreen'].bl.obl.move_list.add_widget(mmo)
            gl.theme_elements['MainScreen'].bl.obl.move_list.la.text = 'New game'

class Clock(): 
    def __init__(self, clock) -> None:
        self.starttime = time.time()
        self.totaltime = 0
        self.started = False
        self.clockWidget = clock

    def clock(self):
        while self.totaltime<time_control and self.started:
            self.totaltime = round((time.time() - self.starttime), 2)
            mins, secs = math.ceil((time_control-self.totaltime+1)/60)-1, math.ceil(time_control-self.totaltime)%60
            timeformat= '{:02d}:{:02d}'.format(mins,secs)
            self.clockWidget.text = timeformat
            time.sleep(0.02)
        if self.totaltime >= time_control:
            Frontend.invoke_popup(f'{"Black" if white_to_move else "White"} won on time.')
            Frontend.reset_game()
            return

    def toggle(self):
        global time_control, increment
        if not self.started:
            self.starttime = time.time() - self.totaltime
            self.started = True
            Thread(target=self.clock).start()
        else:
            self.started = False
            self.totaltime -= increment
            self.clockWidget.text = '{:02d}:{:02d}'.format(math.ceil((time_control-self.totaltime+1)/60)-1, math.ceil(time_control-self.totaltime)%60)
        return

class Backend():
    def get_all_legal_moves(white:bool, attsquares=False, last_move=None, checkk=None) -> np.ndarray:
        '''
        ### This function generates the legal moves in the current position
        #### Each legal move is in the following format:
        ##### index from: 6 bits, index to: 6 bits, flag: 4 bits
        ##### ex. 0b0011000111000001 would be the move e2-e4 with the normal flag
        '''
        global white_king_bitboard, black_king_bitboard, white_queen_bitboard, black_queen_bitboard, white_bishop_bitboard, black_bishop_bitboard, white_knight_bitboard, black_knight_bitboard, white_rook_bitboard, black_rook_bitboard, white_pawn_bitboard, black_pawn_bitboard
        global black_total_bitboard, white_total_bitboard, attacking_bitboard, king_attack_bitboard, pin_bitboard
        global check
        global bitboard_name_to_pieceClass
        global en_passant_target_index

        legal_moves = np.zeros(shape=218, dtype=np.int32)
        counter = 0
        en_passant_target_index = 0
        white_pieces, black_pieces = Backend.black_and_white_pieces_list()
        multiplier = 1 if white else -1
        color_total_bitboard = black_total_bitboard if white else white_total_bitboard
        total_bitboard = white_total_bitboard | black_total_bitboard

        for piece in (white_pieces if white else black_pieces):
            index = int(piece.text)-1
            row, file = Utils.button_to_rowfile(piece)

            # Get the piece class based on the bitboard it's in
            pieceClass = None
            for name in list(bitboard_name_to_pieceClass.keys()):
                board = globals()[name]
                if Backend.check_index_overlap(board, index):
                    pieceClass = bitboard_name_to_pieceClass[name]

            if issubclass(type(pieceClass), (w.Pawn, b.Pawn)):
                # En passant
                if len(moves_list) > 0:
                    lastmove = last_move if last_move else moves_list[-1]
                    lastmovestr = f'{lastmove:016b}'
                    lmfrom, lmto = int(lastmovestr[0:6], 2), int(lastmovestr[6:12], 2) # lm is an abbreviation for last move
                    _, lmtofile = Utils.index_to_rowfile(lmto)
                    lmpieceClass = None
                    for name in list(bitboard_name_to_pieceClass.keys()):
                        board = globals()[name]
                        if Backend.check_index_overlap(board, lmto):
                            lmpieceClass = bitboard_name_to_pieceClass[name]
                    if lmto == index+1 and file < 7 and abs(lmfrom - lmto) == 16 and isinstance(lmpieceClass, w.Pawn if not white else b.Pawn) and lmtofile-file == 1:
                        ofile, orow = pieceClass.movement[2][0]
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['e'], attsquares)
                        en_passant_target_index = 8*(row+orow)+(file+ofile)
                        counter += 1
                    if lmto == index-1 and file > 0 and abs(lmfrom - lmto) == 16 and isinstance(lmpieceClass, w.Pawn if not white else b.Pawn) and lmtofile-file == -1:
                        ofile, orow = pieceClass.movement[3][0]
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['e'], attsquares)
                        en_passant_target_index = 8*(row+orow)+(file+ofile)
                        counter += 1
                # Capture
                if (Backend.check_index_overlap(color_total_bitboard, index+(9 if white else -7)) or attsquares) and file < 7:
                    ofile, orow = pieceClass.movement[2][0]
                    if row+orow == (7 if white else 0):
                        # Take and promote
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qq'], attsquares)
                        legal_moves[counter+1] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qr'], attsquares)
                        legal_moves[counter+2] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qb'], attsquares)
                        legal_moves[counter+3] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qn'], attsquares)
                        counter += 4
                    else:
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['c'], attsquares)
                        counter += 1
                if (Backend.check_index_overlap(color_total_bitboard, index+(7 if white else -9)) or attsquares) and file > 0:
                    ofile, orow = pieceClass.movement[3][0]
                    if row+orow == (7 if white else 0):
                        # Take and promote
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qq'], attsquares)
                        legal_moves[counter+1] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qr'], attsquares)
                        legal_moves[counter+2] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qb'], attsquares)
                        legal_moves[counter+3] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['qn'], attsquares)
                        counter += 4
                    else:
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['c'], attsquares)
                        counter += 1
                # Normal move
                if not Backend.check_index_overlap(total_bitboard, index+8*multiplier) and not attsquares:
                    ofile, orow = pieceClass.movement[1][0]
                    if row+orow == (7 if white else 0):
                        # Take and promote
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['pq'], attsquares)
                        legal_moves[counter+1] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['pr'], attsquares)
                        legal_moves[counter+2] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['pb'], attsquares)
                        legal_moves[counter+3] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['pn'], attsquares)
                        counter += 4
                    else:
                        legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['n'], attsquares)
                        counter += 1
                        # First move
                        if not Backend.check_index_overlap(total_bitboard, index+16*multiplier) and row == (1 if white else 6):
                            ofile, orow = pieceClass.movement[0][0]
                            legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['n'], attsquares)
                            counter += 1
            elif issubclass(type(pieceClass), (w.King, b.King)):
                white_king = isinstance(pieceClass, w.King)
                # Castle kingside
                if ((white_king and not white_king_moved and not white_krook_moved) or (not white_king and not black_king_moved and not black_krook_moved))\
                and not Backend.check_index_overlap(total_bitboard, index+1) and not Backend.check_index_overlap(total_bitboard, index+2)\
                and not Backend.check_index_overlap(attacking_bitboard, index+1) and not Backend.check_index_overlap(attacking_bitboard, index+2):
                    ofile, orow = pieceClass.movement[1][0]
                    oofile, oorow = pieceClass.movement[1][1]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['k'], attsquares)
                    legal_moves[counter+1] = Backend.move_to_int(row, file, row+oorow, file+oofile, legal_moves_flags['k'], attsquares)
                    counter += 2
                # Castle queenside
                if ((white_king and not white_king_moved and not white_qrook_moved) or (not white_king and not black_king_moved and not black_qrook_moved))\
                and not Backend.check_index_overlap(total_bitboard, index-1) and not Backend.check_index_overlap(total_bitboard, index-2) and not Backend.check_index_overlap(total_bitboard, index-3)\
                and not Backend.check_index_overlap(attacking_bitboard, index-1) and not Backend.check_index_overlap(attacking_bitboard, index-2) and not Backend.check_index_overlap(attacking_bitboard, index-3):
                    ofile, orow = pieceClass.movement[0][0]
                    oofile, oorow = pieceClass.movement[0][1]
                    legal_moves[counter] = Backend.move_to_int(row, file, row+orow, file+ofile, legal_moves_flags['q'], attsquares)
                    legal_moves[counter+1] = Backend.move_to_int(row, file, row+oorow, file+oofile, legal_moves_flags['q'], attsquares)
                    counter += 2
                # The rest of the moves
                for i in range(2, 10):
                    f, r = pieceClass.movement[i][0]
                    fto, rto = file+f, row+r
                    if fto > 7 or fto < 0 or rto > 7 or rto < 0:
                        continue
                    if Backend.check_index_overlap(color_total_bitboard, index+(8*r+f)):
                        legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['c'], attsquares)
                        counter += 1
                    elif not Backend.check_index_overlap(total_bitboard, index+(8*r+f)):
                        legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['n'], attsquares)
                        counter += 1
            else:
                for direction in pieceClass.movement:
                    for option in direction:
                        f, r = option
                        fto, rto = file+f, row+r
                        if fto > 7 or fto < 0 or rto > 7 or rto < 0:
                            break
                        if not Backend.check_index_overlap(total_bitboard, index+(8*r+f)):
                            legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['n'], attsquares)
                            counter += 1
                        elif Backend.check_index_overlap(color_total_bitboard, index+(8*r+f)):
                            legal_moves[counter] = Backend.move_to_int(row, file, rto, fto, legal_moves_flags['c'], attsquares)
                            counter += 1
                            break
                        else:
                            break

        if counter == 0:
            return
        legal_moves = np.resize(legal_moves, counter)
        if attsquares:
            return legal_moves
        
        # Check every move to see if it's pinned and remove any moves that leaves the kng in check
        # Also, check if any king move walks into check
        possible_moves = np.zeros(shape=218, dtype=np.int32)
        p_counter = 0
        for move in legal_moves:
            s_index, t_index, flag = Utils.move_to_fi_ti_flag(move)
            if Backend.check_index_overlap(white_king_bitboard if white else black_king_bitboard, s_index):
                if flag == 'c':
                    sname, tname = Backend.make_unmake_move(s_index, t_index, flag, white)
                    lm = Backend.get_all_legal_moves(not white, attsquares=True)
                    if np.where(lm == t_index)[0].size == 0:
                        possible_moves[p_counter] = move
                        p_counter += 1
                    Backend.make_unmake_move(s_index, t_index, flag, white, sname=sname, tname=tname)
                    continue
                if not Backend.check_index_overlap(attacking_bitboard, t_index):
                    if check or checkk:
                        sname, tname = Backend.make_unmake_move(s_index, t_index, flag, white)
                        lm = Backend.get_all_legal_moves(not white, attsquares=True)
                        if np.where(lm == t_index)[0].size == 0:
                            possible_moves[p_counter] = move
                            p_counter += 1
                        Backend.make_unmake_move(s_index, t_index, flag, white, sname=sname, tname=tname)
                        continue
                    possible_moves[p_counter] = move
                    p_counter += 1
                    continue
                else:
                    continue
            
            # If the king is in check and it needs to move, the previous if-statement will also
            # result in True, so we only have to check if other pieces can block
            if check or checkk:
                if flag in ['c', 'e'] or (flag[0]=='q' and len(flag) == 2):
                    sname, tname = Backend.make_unmake_move(s_index, t_index, flag, white)
                    lm = Backend.get_all_legal_moves(not white, attsquares=True)
                    if np.where(lm == (white_king_index if white else black_king_index))[0].size == 0:
                        possible_moves[p_counter] = move
                        p_counter += 1
                    Backend.make_unmake_move(s_index, t_index, flag, white, sname=sname, tname=tname)
                    continue
                if Backend.check_index_overlap(king_attack_bitboard, t_index) and Backend.check_index_overlap(pin_bitboard, t_index):
                    sname, tname = Backend.make_unmake_move(s_index, t_index, flag, white)
                    lm = Backend.get_all_legal_moves(not white, attsquares=True)
                    if np.where(lm == (white_king_index if white else black_king_index))[0].size == 0:
                        possible_moves[p_counter] = move
                        p_counter += 1
                    Backend.make_unmake_move(s_index, t_index, flag, white, sname=sname, tname=tname)
                    continue
                else:
                    continue

            if not Backend.check_index_overlap(pin_bitboard, s_index):
                possible_moves[p_counter] = move
                p_counter += 1
                continue
            if Backend.check_index_overlap(pin_bitboard, t_index):
                possible_moves[p_counter] = move
                p_counter += 1
                continue
        legal_moves = np.resize(possible_moves, p_counter)
        return legal_moves

    def legal_moves_per_square(moves:np.ndarray) -> None:
        global legal_moves_per_square
        legal_moves_per_square = {}
        moves_dict = {}
        for move in moves:
            movestr = f'{move:016b}'
            s_index = int(movestr[0:6], 2)
            if s_index in moves_dict:
                moves_dict[s_index].append(move)
                continue
            moves_dict[s_index] = [move]
        legal_moves_per_square = deepcopy(moves_dict)
        return
    
    def mate_and_draw(move:int) -> tuple[bool, str]:
        global check, legal_moves_per_square, repitition, fiftymoverule
        global moves_posfen
        if check and not legal_moves_per_square:
            return True, ''
        elif not legal_moves_per_square:
            return False, 'stalemate'
        _, ti, flag = Utils.move_to_fi_ti_flag(move)
        try:
            if flag in ['c', 'e', 'qq', 'qr', 'qb', 'qn'] or issubclass(Utils.get_piece_type(ti), (w.Pawn, b.Pawn)):
                fiftymoverule = 0
            else:
                fiftymoverule += 1
        except:
            fiftymoverule += 1
        if fiftymoverule >= 50:
            return False, '50-move rule'
        if moves_posfen:
            if moves_posfen.count(max(set(moves_posfen), key=moves_posfen.count)) == 3:
                return False, 'threefold repitition'
        typeList = Misc.piecesTypesList()
        white_insufficient = (typeList.count(w.Pawn) == 0 and typeList.count(w.Queen) == 0 and typeList.count(w.Rook) == 0 and typeList.count(w.Knight) + typeList.count(w.Bishop) <= 1)
        black_insufficient = (typeList.count(b.Pawn) == 0 and typeList.count(b.Queen) == 0 and typeList.count(b.Rook) == 0 and typeList.count(b.Knight) + typeList.count(b.Bishop) <= 1)
        if white_insufficient and black_insufficient:
            return False, 'insufficient material'
        return False, ''
    
    def make_unmake_move(s_index:int, t_index:int, flag:str, white:bool, sname=None, tname=None) -> tuple[str, str] | None:
        global white_king_bitboard, black_king_bitboard, white_queen_bitboard, black_queen_bitboard, white_bishop_bitboard, black_bishop_bitboard, white_knight_bitboard, black_knight_bitboard, white_rook_bitboard, black_rook_bitboard, white_pawn_bitboard, black_pawn_bitboard
        global white_total_bitboard, black_total_bitboard, piece_bitboards
        global piece_bitboards
        s_pieceBitboard, t_pieceBitboard = None, None
        if not (sname or tname):
            snamee, tnamee = None, None
            for name in piece_bitboards:
                board = globals()[name]
                if Backend.check_index_overlap(board, s_index):
                    s_pieceBitboard = board
                    snamee = name
                elif Backend.check_index_overlap(board, (t_index+8*(-1 if white else 1) if flag=='e' else t_index)):
                    t_pieceBitboard = board
                    tnamee = name
        else:
            if sname:
                s_pieceBitboard = globals()[sname]
            if tname:
                t_pieceBitboard = globals()[tname]
        if flag in ['c', 'e']:
            # Capture
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, t_index)
            t_pieceBitboard = Utils.toggle_bit(t_pieceBitboard, t_index)
        # Promotion
        elif flag in ['pq', 'qq']:
            p_pieceBitboard = white_queen_bitboard if white else black_queen_bitboard
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            if flag[0] == 'q':
                t_pieceBitboard = Utils.toggle_bit(t_pieceBitboard, t_index)
            p_pieceBitboard = Utils.toggle_bit(p_pieceBitboard, t_index)
        elif flag in ['pr', 'qr']:
            p_pieceBitboard = white_rook_bitboard if white else black_rook_bitboard
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            if flag[0] == 'q':
                t_pieceBitboard = Utils.toggle_bit(t_pieceBitboard, t_index)
            p_pieceBitboard = Utils.toggle_bit(p_pieceBitboard, t_index)
        elif flag in ['pb', 'qr']:
            p_pieceBitboard = white_bishop_bitboard if white else black_bishop_bitboard
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            if flag[0] == 'q':
                t_pieceBitboard = Utils.toggle_bit(t_pieceBitboard, t_index)
            p_pieceBitboard = Utils.toggle_bit(p_pieceBitboard, t_index)
        elif flag in ['pn', 'qn']:
            p_pieceBitboard = white_knight_bitboard if white else black_knight_bitboard
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            if flag[0] == 'q':
                t_pieceBitboard = Utils.toggle_bit(t_pieceBitboard, t_index)
            p_pieceBitboard = Utils.toggle_bit(p_pieceBitboard, t_index)
        else:
            # Normal move
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, s_index)
            s_pieceBitboard = Utils.toggle_bit(s_pieceBitboard, t_index)
        if sname or tname:
            globals()[sname] = deepcopy(s_pieceBitboard)
            globals()[tname] = deepcopy(t_pieceBitboard)
            white_total_bitboard = deepcopy(white_bishop_bitboard | white_king_bitboard | white_knight_bitboard | white_rook_bitboard | white_queen_bitboard | white_pawn_bitboard)
            black_total_bitboard = deepcopy(black_bishop_bitboard | black_king_bitboard | black_knight_bitboard | black_rook_bitboard | black_queen_bitboard | black_pawn_bitboard)
            return
        if snamee:
            globals()[snamee] = deepcopy(s_pieceBitboard)
        if tnamee:
            globals()[tnamee] = deepcopy(t_pieceBitboard)
        white_total_bitboard = deepcopy(white_bishop_bitboard | white_king_bitboard | white_knight_bitboard | white_rook_bitboard | white_queen_bitboard | white_pawn_bitboard)
        black_total_bitboard = deepcopy(black_bishop_bitboard | black_king_bitboard | black_knight_bitboard | black_rook_bitboard | black_queen_bitboard | black_pawn_bitboard)
        return snamee, tnamee
    
    # Checks if the index given is 1 in the given bitboard
    def check_index_overlap(board:int, index:int) -> bool:
        '''
        Checks if the given index is 1 in the given bitboard.
        It shifts the board over by the index and performs a bitwise AND operation on the result and 1
        '''
        return board >> index & 1 == 1

    def move_to_int(row:int, file:int, rto:int, fto:int, flag:int, attsquare:bool) -> int:
        if attsquare:
            return 8*rto+fto
        return int(f'0b{8*row+file:06b}{8*rto+fto:06b}{flag:04b}', 2)
    
    def format_legal_moves(legalmoves:list, row:int, file:int) -> list:
        well_formatted = []
        for el in legalmoves:
            move = el[0]
            moveType = el[1]
            i = 8*(row+move[1]) + (file+move[0])
            move_from = f'0{8*row+file}' if 8*row+file<10 else str(8*row+file)
            move_to = f'0{i}' if i<10 else str(i)
            well_formatted.append(move_from + move_to + moveType)
        return well_formatted
    
    def black_and_white_pieces_list() -> tuple[list, list]:
        white_pieces = []
        black_pieces = []
        for i in range(64):
            if Backend.check_index_overlap(white_total_bitboard, i):
                white_pieces.append(board[i])
            if Backend.check_index_overlap(black_total_bitboard, i):
                black_pieces.append(board[i])
        return white_pieces, black_pieces

    def update_bitboards(white:bool):
        global white_bishop_bitboard, white_king_bitboard, white_knight_bitboard, white_pawn_bitboard, white_queen_bitboard, white_rook_bitboard, black_bishop_bitboard, black_king_bitboard, black_knight_bitboard, black_pawn_bitboard, black_queen_bitboard, black_rook_bitboard
        global white_total_bitboard, black_total_bitboard, attacking_bitboard, king_attack_bitboard, pin_bitboard
        white_bishop_bitboard = 0
        white_king_bitboard = 0
        white_knight_bitboard = 0
        white_pawn_bitboard = 0
        white_queen_bitboard = 0
        white_rook_bitboard = 0
        black_bishop_bitboard = 0
        black_king_bitboard = 0
        black_knight_bitboard = 0
        black_pawn_bitboard = 0
        black_queen_bitboard = 0
        black_rook_bitboard = 0
        white_total_bitboard = 0
        black_total_bitboard = 0
        attacking_bitboard = 0
        king_attack_bitboard = 0
        pin_bitboard = 0
        for i,row in enumerate(piecesLayout):
            for j,square in enumerate(row):
                if square == None:
                    continue
                else:
                    if isinstance(square, w.Pawn):
                        white_pawn_bitboard = Utils.toggle_bit(white_pawn_bitboard, 8*i+j)
                    elif isinstance(square, b.Pawn):
                        black_pawn_bitboard = Utils.toggle_bit(black_pawn_bitboard, 8*i+j)
                    elif isinstance(square, w.Rook):
                        white_rook_bitboard = Utils.toggle_bit(white_rook_bitboard, 8*i+j)
                    elif isinstance(square, b.Rook):
                        black_rook_bitboard = Utils.toggle_bit(black_rook_bitboard, 8*i+j)
                    elif isinstance(square, w.Knight):
                        white_knight_bitboard = Utils.toggle_bit(white_knight_bitboard, 8*i+j)
                    elif isinstance(square, b.Knight):
                        black_knight_bitboard = Utils.toggle_bit(black_knight_bitboard, 8*i+j)
                    elif isinstance(square, w.Bishop):
                        white_bishop_bitboard = Utils.toggle_bit(white_bishop_bitboard, 8*i+j)
                    elif isinstance(square, b.Bishop):
                        black_bishop_bitboard = Utils.toggle_bit(black_bishop_bitboard, 8*i+j)
                    elif isinstance(square, w.Queen):
                        white_queen_bitboard = Utils.toggle_bit(white_queen_bitboard, 8*i+j)
                    elif isinstance(square, b.Queen):
                        black_queen_bitboard = Utils.toggle_bit(black_queen_bitboard, 8*i+j)
                    elif isinstance(square, w.King):
                        white_king_bitboard = Utils.toggle_bit(white_king_bitboard, 8*i+j)
                    elif isinstance(square, b.King):
                        black_king_bitboard = Utils.toggle_bit(black_king_bitboard, 8*i+j)
        white_total_bitboard = white_bishop_bitboard | white_king_bitboard | white_knight_bitboard | white_rook_bitboard | white_queen_bitboard | white_pawn_bitboard
        black_total_bitboard = black_bishop_bitboard | black_king_bitboard | black_knight_bitboard | black_rook_bitboard | black_queen_bitboard | black_pawn_bitboard
        Backend.attack_pin_bitboard(white)

    def attack_pin_bitboard(white:bool):
        global attacking_bitboard, king_attack_bitboard, pin_bitboard
        typesLayout = {}
        for i in range(64):
            pieceType = Utils.get_piece_type(i)
            if pieceType is not None:
                typesLayout[i] = pieceType
        
        for attsquare in Backend.get_all_legal_moves(not white, attsquares=True):
            attsquare = attsquare.item()
            attacking_bitboard |= (1<<attsquare)

        # NOTE: Only check sliding pieces (bishop, rook, queen)
        pin_check = [i for i,square in typesLayout.items() if issubclass(square, (b.Bishop, b.Rook, b.Queen) if white else (w.Bishop, w.Rook, w.Queen))]
        if not pin_check:
            pin_bitboard = 0
            return
        for square in pin_check:
            pin_bitboard |= Backend.get_pin_along_sliding_piece(not white, square)
            # King attack
            king_attack_bitboard |= Backend.get_pin_along_sliding_piece(not white, square, king_attack=True)

    def get_pin_along_sliding_piece(white:bool, square:int, king_attack=False) -> int:
        pinnypinny = 0
        row, file = Utils.index_to_rowfile(square)
        pieceClass = Utils.get_piece_type(square)()
        color_total_bitboard = white_total_bitboard if white else black_total_bitboard
        opponent_total_bitboard = black_total_bitboard if white else white_total_bitboard
        opponent_king_bitboard = black_king_bitboard if white else white_king_bitboard
        for direction in pieceClass.movement:
            pinned_pieces = 0
            tmp_pin_bitboard = Utils.toggle_bit(0, square)
            for option in direction:
                f, r = option
                fto, rto = file+f, row+r
                if pinned_pieces > 1:
                    break
                if fto > 7 or fto < 0 or rto > 7 or rto < 0:
                    break
                if Backend.check_index_overlap(color_total_bitboard, square+(8*r+f)):
                    break
                elif Backend.check_index_overlap(opponent_king_bitboard, square+(8*r+f)):
                    if pinned_pieces != 1 and not king_attack:
                        break
                    pinnypinny = pinnypinny | tmp_pin_bitboard
                    break
                elif Backend.check_index_overlap(opponent_total_bitboard, square+(8*r+f)):
                    pinned_pieces += 1
                    tmp_pin_bitboard = Utils.toggle_bit(tmp_pin_bitboard, square+(8*r+f))
                else:
                    tmp_pin_bitboard = Utils.toggle_bit(tmp_pin_bitboard, square+(8*r+f))
        return pinnypinny
        
    def update_pieces_layout():
        global board
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
    
    def load_fen(fen:str) -> None|str:
        global fiftymoverule, white_to_move
        global white_king_moved, black_king_moved
        global white_king_index, black_king_index
        global board
        global check
        pieces_fen = {
            'K': w.King(),
            'N': w.Knight(),
            'P': w.Pawn(),
            'Q': w.Queen(),
            'R': w.Rook(),
            'B': w.Bishop(),
            'k': b.King(),
            'n': b.Knight(),
            'p': b.Pawn(),
            'q': b.Queen(),
            'r': b.Rook(),
            'b': b.Bishop()
        }
        counter = 0
        posfen, white_move, castle, _, fiftymovecounter, _ = fen.split(' ', maxsplit=100)
        white_to_move = white_move == 'w'
        white_king_moved = not castle.find('KQ') > -1
        black_king_moved = not castle.find('kq') > -1
        fiftymoverule = int(fiftymovecounter)
        if posfen.count('K') != 1 or posfen.count('k') != 1:
            return 'error'
        for el in board:
            el.image.source = ''
        for l in posfen:
            if l == '/':
                continue
            elif l in ['1', '2', '3', '4', '5', '6', '7', '8']:
                for i in range(int(l)):
                    board[(56-8*(counter//8))+counter%8].image.source = os.path.dirname(__file__) + "\\data\\img\\empty.png"
                    counter += 1
            else:
                board[(56-8*(counter//8))+counter%8].image.source = pieces_fen[l].imgPath.format(gl.user_piece_set)
                counter += 1
        Backend.update_pieces_layout()
        Backend.update_bitboards(white_move == 'w')
        white_king_index = int(math.log2(white_king_bitboard))
        black_king_index = int(math.log2(black_king_bitboard))
        check = Backend.check_index_overlap(attacking_bitboard, white_king_index if white_move == 'w' else black_king_index)
        lm = Backend.get_all_legal_moves(white_to_move)
        Backend.legal_moves_per_square(lm)
        return

class Utils():
    def toggle_bit(board:int, i:int) -> int:
        return board ^ (1<<i)

    def button_to_rowfile(button:Button) -> tuple[int, int]:
        return math.floor((int(button.text)-1)/8), (int(button.text)-1)%8

    def index_to_rowfile(i: int) -> tuple[int, int]:
        return math.floor(i/8), i%8
    
    def rowfile_to_index(row:int, file:int) -> int:
        return 8*row+file
    
    def move_to_fi_ti_flag(move:int) -> tuple[int, int, str]:
        global legal_moves_flags
        movestr = f'{move:016b}'
        return int(movestr[0:6], 2), int(movestr[6:12], 2), list(legal_moves_flags.keys())[list(legal_moves_flags.values()).index(int(movestr[12:], 2))]
    
    def get_piece_type(i:int):
        global piece_bitboards, bitboard_name_to_pieceClass
        for name in piece_bitboards:
            board = globals()[name]
            if Backend.check_index_overlap(board, i):
                return type(bitboard_name_to_pieceClass[name])

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
        for i in range(64):
            pieceType = Utils.get_piece_type(i)
            if pieceType:
                pretty += f'|{pieces_unicode[pieceType]} '
            else:
                pretty += '|  '
            if i % 8 == 7:
                pretty += '|\n-------------------------\n'
        print(pretty, end='\r')

    def position_to_fen() -> tuple[str, str]:
        global en_passant_target_index, fiftymoverule
        '''
        Gives the FEN of the current position. Returns [FEN, FEN with only the position]
        '''
        pieces_fen={
            w.King: 'K',
            w.Knight: 'N',
            w.Pawn: 'P',
            w.Queen: 'Q',
            w.Rook: 'R',
            w.Bishop: 'B',
            b.King: 'k',
            b.Knight: 'n',
            b.Pawn: 'p',
            b.Queen: 'q',
            b.Rook: 'r',
            b.Bishop: 'b'
        }
        file_letters = 'abcdefgh'
        fen = ''
        empty_count = 0
        for i in range(64):
            if i%8==0 and i != 63 and i != 0:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                fen += '/'
            pieceType = Utils.get_piece_type((56-8*(i//8))+i%8)
            if pieceType:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                fen += pieces_fen[pieceType]
            else:
                empty_count += 1
        posfen = deepcopy(fen)
        castle = '-'
        if not white_king_moved:
            if not black_king_moved: castle = 'KQkq'
            else: castle = 'KQ'
        elif not black_king_moved:
            castle = 'kq'
        erow, efile = Utils.index_to_rowfile(en_passant_target_index)
        enpassant = file_letters[efile] + str(erow) if en_passant_target_index != 0 else '-'
        fen += f" {'w' if white_to_move else 'b'} {castle} {enpassant} {fiftymoverule} {math.ceil((movenum+1)/2)}"
        return fen, posfen