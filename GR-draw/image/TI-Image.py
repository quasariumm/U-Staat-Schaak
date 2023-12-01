from ti_image import *

def draw_piece(name, i):
    load_image(name)
    show_image(97+23*(i%8), 24+23*(i//8))

clear-image()
load_image("BR")
show_image(97,24,) #Upper-left corner!