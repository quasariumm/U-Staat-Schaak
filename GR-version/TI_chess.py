from ti_draw import * #ti_draw in Modul, [math], shape/controls, eindig met show_draw, clear for removing starter screen
from ti_image import *
from ti_system import * #The screen is 318x212 pixels and the color values must be integers in the domain [0..255].
from time import * #moet nog gemaakt worden

# Format: [h8, g8, ..., b1, a1]
piecesLayout = ["BR", "BN", "BB", "BK", "BQ", "BB", "BN", "BR","BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP",None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None,"WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP","WR", "WN", "WB", "WK", "WQ", "WB", "WN", "WR"]

select_index = 56
selected_index = None

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

clear()
set_color(87,87,87)
fill_rect(0,0,400,400)
draw_rect(0,0,400,400)
for i in range(64):
    fill_square(i)
set_color(88,100,120)
fill_rect(2,14,92,184)
set_color(255,255,255)
draw_text(4,40,"1.bxa8=Q+")
draw_text(265,40,"10:00")
draw_text(265,195,"10:00")
i = 0
for img in piecesLayout:
    if img:
        place_piece(img, i)
    i += 1
set_color(0,255,255)
draw_rect(95,169,21,21)
while True:
    key = wait_key()
    if key == 1 and select_index%8 != 7: # Right arrow
        set_square_color(select_index)
        draw_rect(95+(select_index%8)*21, 22+(select_index//8)*21, 21, 21)
        set_color(0,255,255)
        draw_rect(95+((select_index+1)%8)*21, 22+((select_index+1)//8)*21, 21, 21)
        select_index = select_index + 1
    elif key == 2 and select_index%8 != 0: # Left arrow
        set_square_color(select_index)
        draw_rect(95+(select_index%8)*21, 22+(select_index//8)*21, 21, 21)
        set_color(0,255,255)
        draw_rect(95+((select_index-1)%8)*21, 22+((select_index-1)//8)*21, 21, 21)
        select_index = select_index - 1
    elif key == 3 and select_index//8 != 0: # Up arrow
        set_square_color(select_index)
        draw_rect(95+(select_index%8)*21, 22+(select_index//8)*21, 21, 21)
        set_color(0,255,255)
        draw_rect(95+((select_index-8)%8)*21, 22+((select_index-8)//8)*21, 21, 21)
        select_index = select_index - 8
    elif key == 4 and select_index//8 != 7: # Down arrow
        set_square_color(select_index)
        draw_rect(95+(select_index%8)*21, 22+(select_index//8)*21, 21, 21)
        set_color(0,255,255)
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
            place_piece(piecesLayout[selected_index], selected_index)
            if select_index != selected_index:
                draw_rect(95+(selected_index%8)*21, 22+(selected_index//8)*21, 21, 21)
            selected_index = None
        else:
            if piecesLayout[select_index] != None:
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
