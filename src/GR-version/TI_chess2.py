from ti_draw import set_color, fill_rect, draw_rect, clear, draw_text
from ti_image import load_image, show_image
from ti_system import wait_key #The screen is 318x212
from time import sleep

lastmovedelta = 0
lastmovetarget = 0
white_to_move = True

whiteBitboard = 0x0
blackBitboard = 0x0
totalBitboard = 0x0

select_index = 56
selected_index = None

legal_moves = []

# Fontend
def set_right_color(i):
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
        return
    set_color(228,217,202)

def fill_square(i):
    fill_rect(58 + 25*(i%8), 5 + 25*(i//8), 27, 27)

def place_piece(white, i):
    load_image("WP" if white else "BP")
    show_image(63+25*(i%8), 10+25*(i//8))

def select_init():
    global select_index, selected_index
    if select_index == selected_index:
        set_color(0,0,255)
    else:
        set_right_color(select_index)
    draw_rect(59+(select_index%8)*25, 6+(select_index//8)*25, 25, 25)
    set_color(0,255,255)

def make_move(move):
    global lastmovetarget, lastmovedelta, white_to_move
    global whiteBitboard, blackBitboard, totalBitboard

    player = whiteBitboard if white_to_move else blackBitboard
    opponent = blackBitboard if white_to_move else whiteBitboard

    player |= 1<<move[1]
    player ^= 1<<move[0]
    fill_square(move[0])
    fill_square(move[1])
    place_piece(white_to_move, move[1])
    if move[2] == 'e':
        ep_vanish = move[1] + 8*(1 if white_to_move else -1) # The pawn gets sent to another dimension
        opponent ^= 1<<ep_vanish
        fill_square(ep_vanish)
    lastmovedelta = abs(move[1]-move[0])
    lastmovetarget = move[1]
    if move[1]//8 == (0 if white_to_move else 7):
        print('{} won!'.format("White" if white_to_move else "Black"))
        sleep(3)
        init()
        return
    white_to_move = not white_to_move
    totalBitboard = whiteBitboard | blackBitboard
    get_all_legal_moves(white_to_move)

def askCorrect():
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
    global legal_moves, whiteBitboard, blackBitboard, totalBitboard
    legal_moves = []
    multiplier = -1 + 2 * white
    player = whiteBitboard if white else blackBitboard
    opponent = blackBitboard if white else whiteBitboard
    for i in range(64):
        if opponent & (1<<i) or not player & (1<<i):
            continue
        i8m, i16m = i+8*multiplier, i+16*multiplier
        if i%8 > 0:
            if opponent & (1<<(i-1)) and lastmovedelta == 16 and lastmovetarget == i-1:
                legal_moves.append([i,i8m-1,'e'])
            if opponent & (i<<(i8m-1)):
                legal_moves.append([i,i8m-1,None])
        if i%8 < 7:
            if opponent & (1<<(i+1)) and lastmovedelta == 16 and lastmovetarget == i+1:
                legal_moves.append([i,i8m+1,'e'])
            if opponent & (1<<i8m):
                legal_moves.append([i,i8m+1,None])
        if not totalBitboard & (1<<i8m):
            legal_moves.append([i,i8m,None])
            if i//8 == (6 if white else 1):
                if not totalBitboard & (1<<i16m):
                    legal_moves.append([i,i16m,None])
        i += 1

def init():
    global whiteBitboard, blackBitboard, totalBitboard, select_index, selected_index, white_to_move, lastmovetarget
    whiteBitboard = 0xff00
    blackBitboard = 0xff000000000000
    totalBitboard = whiteBitboard | blackBitboard
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
        set_right_color(i)
        fill_square(i)
        if whiteBitboard & (1<<i):
            place_piece(True, i)
        elif blackBitboard & (1<<i):
            place_piece(False, i)
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
                place_piece(whiteBitboard & (1<<selected_index), selected_index)
                if select_index != selected_index:
                    draw_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
            selected_index = None
        else:
            if (whiteBitboard & (1<<select_index) and white_to_move) or (blackBitboard & (1<<select_index) and not white_to_move):
                selected_index = select_index
                set_color(0,0,255)
                fill_rect(59+(selected_index%8)*25, 6+(selected_index//8)*25, 25, 25)
                place_piece(whiteBitboard & (1<<selected_index), select_index)