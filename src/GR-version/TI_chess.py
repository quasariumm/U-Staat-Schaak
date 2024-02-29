from ti_draw import set_color, fill_rect, draw_rect, clear, draw_text
from ti_image import load_image, show_image
from ti_system import wait_key #The screen is 318x212
from time import sleep

lastmovedelta : int = 0
lastmovetarget : int = 0
white_to_move : bool = True
piecesLayout : list[str|None] = []

select_index : int = 56
selected_index : int|None = None

legal_moves : list[list[int|str]] = []

# Fontend
def set_right_color(i) -> None:
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
        return
    set_color(228,217,202)

def fill_square(i) -> None:
    pos = (59+(i%8)*25, 6+(i//8)*25)
    fill_rect(pos[0]-1, pos[1]-1, 27, 27)

def place_piece(name, i) -> None:
    load_image(name)
    show_image(63+25*(i%8), 10+25*(i//8))

def select_init() -> None:
    global select_index, selected_index
    if select_index == selected_index:
        set_color(0,0,255)
    else:
        set_right_color(select_index)
    draw_rect(59+(select_index%8)*25, 6+(select_index//8)*25, 25, 25)
    set_color(0,255,255)

def make_move(move) -> None:
    global lastmovetarget, lastmovedelta, white_to_move
    piecesLayout[move[1]] = piecesLayout[move[0]]
    piecesLayout[move[0]] = None
    fill_square(move[0])
    fill_square(move[1])
    place_piece('{}P'.format('W' if white_to_move else 'B'), move[1])
    if move[2] == 'e':
        ep_vanish = move[1] + 8*(1 if white_to_move else -1) # The pawn gets sent to another dimension
        piecesLayout[ep_vanish] = None
        fill_square(ep_vanish)
    lastmovedelta = abs(move[1]-move[0])
    lastmovetarget = move[1]
    if move[1]//8 == (0 if white_to_move else 7):
        print('{} won!'.format("White" if white_to_move else "Black"))
        sleep(3)
        init()
        return
    white_to_move = not white_to_move
    get_all_legal_moves(white_to_move)

def askCorrect() -> bool:
    set_color(255,255,255)
    draw_text(156,196,"Valid?")
    set_color(255,150,150)
    draw_text(16,196,"Yes")
    set_color(150,255,150)
    draw_text(256,196,"No")
    wait_key()
    if key == 68: # graph/f5 (key for 'yes')
        return True
    return False

def clearAsk():
    set_color(87,87,87)
    fill_rect(0,196,400,40)

# Backend
def get_all_legal_moves(white:bool):
    global legal_moves
    legal_moves = []
    multiplier = -1 + 2 * white
    opponent = not white
    i = 0
    for piece in piecesLayout:
        if piece is None or piece == opponent:
            i += 1
            continue
        i8m, i16m = i+8*multiplier, i+16*multiplier
        if i%8 > 0:
            if piecesLayout[i-1] == opponent and lastmovedelta == 16 and lastmovetarget == i-1:
                legal_moves.append([i,i8m-1,'e'])
            if piecesLayout[i8m-1] == opponent:
                legal_moves.append([i,i8m-1,None])
        if i%8 < 7:
            if piecesLayout[i+1] == opponent and lastmovedelta == 16 and lastmovetarget == i+1:
                legal_moves.append([i,i8m+1,'e'])
            if piecesLayout[i8m+1] == opponent:
                legal_moves.append([i,i8m+1,None])
        if piecesLayout[i8m] is None:
            legal_moves.append([i,i8m,None])
            if i//8 == (6 if white else 1):
                if piecesLayout[i16m] is None:
                    legal_moves.append([i,i16m,None])
        i += 1

def init():
    global piecesLayout, select_index, selected_index, white_to_move, lastmovetarget
    piecesLayout = [None, None, None, None, None, None, None, None, False, False, False, False, False, False, False, False, None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None, True, True, True, True, True, True, True, True, None, None, None, None, None, None, None, None]
    select_index = 56
    selected_index = None
    white_to_move = True
    lastmovetarget = 0
    get_all_legal_moves(white_to_move)
    clear()
    set_color(87,87,87)
    fill_rect(0,0,400,400)
    draw_rect(0,0,400,400)
    for i in range(64):
        fill_square(i)
    i = 0
    for img in piecesLayout:
        if img is not None:
            place_piece("WP" if img else "BP", i)
        i += 1
    set_color(0,255,255)
    draw_rect(59,181,25,25)

init()
    
while True:
    key = wait_key()
    if key == 1 and select_index%8 != 7: # Right arrow
        select_init()
        draw_rect(59+((select_index+1)%8)*25, 6+((select_index+1)//8)*25, 25, 25)
        select_index = select_index + 1
    elif key == 2 and select_index%8 != 0: # Left arrow
        select_init()
        draw_rect(59+((select_index-1)%8)*25, 6+((select_index-1)//8)*25, 25, 25)
        select_index = select_index - 1
    elif key == 3 and select_index//8 != 0: # Up arrow
        select_init()
        draw_rect(59+((select_index-8)%8)*25, 6+((select_index-8)//8)*25, 25, 25)
        select_index = select_index - 8
    elif key == 4 and select_index//8 != 7: # Down arrow
        select_init()
        draw_rect(59+((select_index+8)%8)*25, 6+((select_index+8)//8)*25, 25, 25)
        select_index = select_index + 8
    elif key == 5: # Enter
        # (un)select the current square
        if selected_index != None:
            set_right_color(selected_index)
            fill_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
            possible_moves = [[selected_index, select_index, None], [selected_index, select_index, 'e']]
            if legal_moves.count(possible_moves[0]) > 0:
                correct = askCorrect()
                clearAsk()
                if not correct:
                    continue
                make_move(possible_moves[0])
            elif legal_moves.count(possible_moves[1]) > 0:
                correct = askCorrect()
                clearAsk()
                if not correct:
                    continue
                make_move(possible_moves[1])
            else:
                place_piece(piecesLayout[selected_index], selected_index)
                if select_index != selected_index:
                    draw_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
            selected_index = None
        else:
            if piecesLayout[select_index] == white_to_move:
                selected_index = select_index
                set_color(0,0,255)
                fill_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
                place_piece(piecesLayout[select_index], select_index)