from funcs import *
# from creagrams import *
from map_obj import *
# from trainer_sprites import *
from map import start_map


def main(_):
    c.curs_set(0)
    _.nodelay(True)
    scr = c.newwin(24, 80, 0, 0)
    graphics = scr.derwin(17, 78, 1, 1)
    text = scr.derwin(4, 52, 19, 1)
    choice = scr.derwin(4, 25, 19, 54)
    scr.immedok(True)
    graphics.immedok(True)
    text.immedok(True)
    choice.immedok(True)
    init_borders(scr)
    scr.refresh()
    scr.keypad(True)
    start_map(graphics, text, choice, (1, 1), (17, 78), (100, 100),
              [InterTest(3, 3)])


c.wrapper(main)
