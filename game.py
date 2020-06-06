from funcs import *
from creagrams import *
from interactive import *
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
    sysnake, prenty = Sysnake(text, 80, 'Starter'), Prenty(text, 80)
    Opponent('X', 'Let\'s battle!', 'I lost...', [prenty], rival_battle_sprite).on_interacted_with(
        Trainer('PLAYER', [sysnake], player_battle_sprite), graphics, text, choice
    )


c.wrapper(main)
