from ti_draw import * #ti_draw in Modul, [math], shape/controls, eindig met show_draw, clear for removing starter screen
from ti_image import *
from ti_system import * #The screen is 318x212 pixels and the color values must be integers in the domain [0..255].
from time import * #moet nog gemaakt worden

def fill_square(i):
    pos = (80+(i%8)*23, 14+(i//8)*23)
    row=i//8+1
    if (i%2==0 if row%2==0 else i%2==1):
        set_color(121,92,52)
    else:
        set_color(228,217,202)
    fill_rect(pos[0], pos[1], 23, 23)

    draw_rect(pos[0],pos[1],21,21)

def place_piece(name, i):
    load_image(name)
    draw_image(97+23*(i%8), 24+23*(i//8))

clear()
set_color(87,87,87)
fill_rect(0,0,500,500)
draw_rect(0,0,500,500)
for i in range(64):
    fill_square(i)
set_color(88,100,120)
fill_rect(0,14,92,184)
draw_rect(0,14,92,184)
set_color(255,255,255)
draw_text(4,40,"1.bxa8=Q+")
draw_text(265,40,"10:00")
draw_text(265,195,"10:00")

show_draw() 
