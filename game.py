from funcs import *
from creagrams import *
from map_obj import *
# from trainer_sprites import *
from map import start_map


def main(_):
    c.curs_set(0)
    scr = c.newwin(24, 80, 0, 0)
    graphics = scr.derwin(17, 78, 1, 1)
    text = scr.derwin(4, 52, 19, 1)
    choice = scr.derwin(4, 25, 19, 54)
    graphics.immedok(True)
    text.immedok(True)
    choice.immedok(True)
    init_borders(scr)
    graphics.keypad(True)
    start_map(graphics, text, choice, (1, 1), (17, 78), (100, 100),
              [GrassPatch(2, 2, 10, 10, [
                  (1, "Prenty"), (.1, "Sysnake")
              ], [49, 50, 51])],
              Player("PLAYER", [Sysnake(text, 30, "Snaky"), Prenty(text, 50)]))


c.wrapper(main)
