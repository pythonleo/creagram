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
    house = Map(12, 12, [MapObject(2, 2, 'a')])
    start_map(graphics, text, choice, (1, 1), (17, 78), (100, 100),
              [MapObject(3, 3, " ______ \n/______\\\n|______|", map=house, pos=(2, 2), exit=(10, 5), transport=(9, 5))],
              Player("PLAYER", [Sysnake(text, 5, "Snaky")]))


c.wrapper(main)
