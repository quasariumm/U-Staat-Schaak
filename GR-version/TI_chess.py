from ti_draw import set_color, fill_rect, draw_rect, clear, draw_text
from ti_image import load_image, show_image
from ti_system import wait_key #The screen is 318x212

lastmovedelta = 0
lastmovetarget = 0
white_to_move = True
piecesLayout = [None, None, None, None, None, None, None, None, "BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP", None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None, "WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP", None, None, None, None, None, None, None, None]

select_index = 56
selected_index = None

legal_moves = []

# Fontend
def fill_square(i):
    pos = (59+(i%8)*25, 6+(i//8)*25)
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
    else:
        set_color(228,217,202)
    fill_rect(pos[0], pos[1], 25, 25)
    draw_rect(pos[0],pos[1],25,25)

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
    show_image(63+25*(i%8), 10+25*(i//8))

def select_init():
    set_square_color(select_index)
    draw_rect(59+(select_index%8)*25, 6+(select_index//8)*25, 25, 25)
    set_color(0,255,255)

def make_move(move):
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
        return
    white_to_move = not white_to_move
    get_all_legal_moves(white_to_move)

# Backend
def get_all_legal_moves(white:bool):
    global legal_moves
    legal_moves = []
    multiplier = -1 if white else 1
    opponent = "BP" if white else "WP"
    i = 0
    for piece in piecesLayout:
        if piece is None or piece == opponent:
            i += 1
            continue
        row, file = index_to_rowfile(i)
        if file > 0:
            if piecesLayout[i-1] == opponent and lastmovedelta == 16 and lastmovetarget == i-1:
                legal_moves.append([i,i+8*multiplier-1,'e'])
            if piecesLayout[i+8*multiplier-1] == opponent:
                legal_moves.append([i,i+8*multiplier-1,None])
        if file < 7:
            if piecesLayout[i+1] == opponent and lastmovedelta == 16 and lastmovetarget == i+1:
                legal_moves.append([i,i+8*multiplier+1,'e'])
            if piecesLayout[i+8*multiplier+1] == opponent:
                legal_moves.append([i,i+8*multiplier+1,None])
        if piecesLayout[i+8*multiplier] == None:
            legal_moves.append([i,i+8*multiplier,None])
            if row == (6 if white else 1):
                if piecesLayout[i+16*multiplier] == None:
                    legal_moves.append([i,i+16*multiplier,None])
        i += 1

# Utils
def index_to_rowfile(i: int) -> tuple[int, int]:
    return i//8, i%8

get_all_legal_moves(white_to_move)

clear()
set_color(87,87,87)
fill_rect(0,0,400,400)
draw_rect(0,0,400,400)
set_color(255,255,255)
for i in range(64):
    fill_square(i)
i = 0
for img in piecesLayout:
    if img:
        place_piece(img, i)
    i += 1
set_color(0,255,255)
draw_rect(59,181,25,25)
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
            row=selected_index//8+1
            if (selected_index%2==0 if row%2==0 else selected_index%2==1):
                set_color(121,92,52)
            else:
                set_color(228,217,202)
            fill_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
            possible_moves = [[selected_index, select_index, None], [selected_index, select_index, 'e']]
            if legal_moves.count(possible_moves[0]) > 0:
                make_move(possible_moves[0])
                selected_index = None
            elif legal_moves.count(possible_moves[1]) > 0:
                make_move(possible_moves[1])
                selected_index = None
            else:
                place_piece(piecesLayout[selected_index], selected_index)
                if select_index != selected_index:
                    draw_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
                selected_index = None
        else:
            if piecesLayout[select_index] == ('WP' if white_to_move else 'BP'):
                selected_index = select_index
                set_color(0,0,255)
                fill_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
                place_piece(piecesLayout[select_index], select_index)