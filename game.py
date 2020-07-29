from funcs import *
from creagrams import *
from map_obj import *
from trainer_sprites import *


def main(_):
    c.curs_set(0)
    scr = c.newwin(24, 80, 0, 0)
    graphics = scr.derwin(17, 78, 1, 1)
    graphics.addstr(0, 0, "WHATEVER'S IN THE OVERWORLD")
    text = scr.derwin(4, 52, 19, 1)
    choice = scr.derwin(4, 25, 19, 54)
    text.immedok(True)
    choice.immedok(True)
    init_borders(scr)
    sysnake = Sysnake(text, 10, 'Starter')
    Opponent((0, 0), 'X', 'Let\'s battle!', 'I lost...', [Prenty(text, 90)],
             rival_battle_sprite).on_interacted_with(
        Trainer((0, 0), 'PLAYER', [sysnake, Prenty(text, 1)], player_battle_sprite), graphics, text, choice
    )


c.wrapper(main)
