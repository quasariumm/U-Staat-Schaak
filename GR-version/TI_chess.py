from ti_draw import set_color, fill_rect, draw_rect, clear, draw_text
from ti_image import load_image, show_image
from ti_system import wait_key #The screen is 318x212
from math import floor

movenum = 0
moves_list = []
lastmovedelta = 0
lastmovetarget = 0
white_to_move = True
piecesLayout = ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, "WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"]

select_index = 56
selected_index = None

legal_moves = []
legal_moves_no_flag = []

# Fontend
def fill_square(i):
    pos = (95+(i%8)*21, 22+(i//8)*21)
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
    else:
        set_color(228,217,202)
    fill_rect(pos[0], pos[1], 21, 21)
    draw_rect(pos[0],pos[1],21,21)
    return

def set_square_color(i):
    if i == selected_index:
        set_color(0,0,255)
        return
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
    else:
        set_color(228,217,202)

def place_piece(name, i):
    load_image(name)
    show_image(97+21*(i%8), 24+21*(i//8))
    return

def make_move(move):
    global lastmovetarget, lastmovedelta, white_to_move
    white = move[1]-move[0] > 0
    piecesLayout[move[1]] = piecesLayout[move[0]]
    piecesLayout[move[0]] = None
    fill_square(move[0])
    fill_square(move[1])
    place_piece('{}P'.format('W' if white else 'B'), move[1])
    if move[2] == 'e':
        ep_vanish = move[1] + 8*(1 if white else -1) # The pawn gets sent to another dimension
        piecesLayout[ep_vanish] = None
        fill_square(ep_vanish)
    lastmovedelta = abs(move[1]-move[0])
    lastmovetarget = move[1]
    white_to_move = not white_to_move
    get_all_legal_moves(white_to_move)

# Backend
def get_all_legal_moves(white:bool):
    # All moves in the following format: [from, to, flag]
    global legal_moves, legal_moves_no_flag
    legal_moves = []
    multiplier = 1 if white else -1
    opponent = "BP" if white else "WP"
    i = 0
    for piece in piecesLayout:
        if piece is None:
            continue
        row, file = index_to_rowfile(i)
        if movenum > 0:
            if piecesLayout[i+1] == opponent and file < 7 and lastmovedelta == 16 and lastmovetarget == i+1:
                legal_moves.append([i+1,i+multiplier,'e'])
            if piecesLayout[i-1] == opponent and file > 0 and lastmovedelta == 16 and lastmovetarget == i-1:
                legal_moves.append([i-1,i+multiplier,'e'])
        if piecesLayout[i+(9 if white else -7)] == opponent and file < 7:
            legal_moves.append([i+1,i+multiplier,'c'])
        if piecesLayout[i+(7 if white else -9)] == opponent and file > 0:
            legal_moves.append([i-1,i+multiplier,'c'])
        if piecesLayout[i+8*multiplier] is not None:
            legal_moves.append([i,i+multiplier,'n'])
            if piecesLayout[i+16*multiplier] is None and row == (0 if white else 7):
                legal_moves.append([i,i+2*multiplier,'n'])
        i += 1
    legal_moves_no_flag = [m[0:2] for m in legal_moves]

# Utils
def index_to_rowfile(i: int) -> tuple[int, int]:
    return floor(i/8), i%8

get_all_legal_moves(white_to_move)

clear()
set_color(87,87,87)
fill_rect(0,0,400,400)
draw_rect(0,0,400,400)
set_color(88,100,120)
fill_rect(2,14,92,184)
set_color(255,255,255)
for i in range(64):
    fill_square(i)
i = 0
for img in piecesLayout:
    if img:
        place_piece(img, i)
    i += 1
set_color(0,255,255)
draw_rect(95,169,21,21)
while True:
    key = wait_key()
    if key > 0 and key <= 4:
        set_square_color(select_index)
        draw_rect(95+(select_index%8)*21, 22+(select_index//8)*21, 21, 21)
        set_color(0,255,255)
    if key == 1 and select_index%8 != 7: # Right arrow
        draw_rect(95+((select_index+1)%8)*21, 22+((select_index+1)//8)*21, 21, 21)
        select_index = select_index + 1
    elif key == 2 and select_index%8 != 0: # Left arrow
        draw_rect(95+((select_index-1)%8)*21, 22+((select_index-1)//8)*21, 21, 21)
        select_index = select_index - 1
    elif key == 3 and select_index//8 != 0: # Up arrow
        draw_rect(95+((select_index-8)%8)*21, 22+((select_index-8)//8)*21, 21, 21)
        select_index = select_index - 8
    elif key == 4 and select_index//8 != 7: # Down arrow
        draw_rect(95+((select_index+8)%8)*21, 22+((select_index+8)//8)*21, 21, 21)
        select_index = select_index + 8
    elif key == 5: # Enter
        # (un)select the current square
        if selected_index != None:
            row=selected_index//8+1
            if (selected_index%2==0 if row%2==0 else selected_index%2==1):
                set_color(121,92,52)
            else:
                set_color(228,217,202)
            fill_rect(95+(selected_index%8)*21, 22+(selected_index//8)*21, 21, 21)
            if [selected_index, select_index] in legal_moves_no_flag:
                make_move(legal_moves[legal_moves_no_flag.index([selected_index, select_index])])
                selected_index = None
            else:
                place_piece(piecesLayout[selected_index], selected_index)
                if select_index != selected_index:
                    draw_rect(95+(selected_index%8)*21, 22+(selected_index//8)*21, 21, 21)
                selected_index = None
        else:
            if piecesLayout[select_index] == ('WP' if white_to_move else 'BP'):
                selected_index = select_index
                set_color(0,0,255)
                fill_rect(95+(selected_index%8)*21, 22+(selected_index//8)*21, 21, 21)
                place_piece(piecesLayout[select_index], select_index)
            
    set_color(88,100,120)
    fill_rect(2,14,92,148)
    set_color(255,255,255)
    draw_text(4,40,str(key))
    draw_text(4,120,str(select_index))
show_draw()
