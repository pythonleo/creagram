from funcs import *
# from sprites import prof_intro
# import json
# import os
from cg_battle import CGBattle
from creagrams import *


def main(_):
    c.curs_set(0)
    scr: c.window = c.newwin(24, 80, 0, 0)
    graphics: c.window = scr.derwin(17, 78, 1, 1)
    text: c.window = scr.derwin(4, 52, 19, 1)
    choice: c.window = scr.derwin(4, 25, 19, 54)
    text.immedok(True)
    choice.immedok(True)
    init_borders(scr)
    sysnake, prenty = Sysnake(text, 100, 'Starter'), Prenty(text, 30)
    my_prenty = Prenty(text, 7, 'Hello')
    '''
    if not os.path.exists('player_info.json'):
        sprite_init(graphics, text, prof_intro)
        add_text(text, 0, 0, "First, are you a boy or a girl?")
        gender = choose(choice, {'q': 'boy', 'e': 'girl'}) == 'q'
        add_text(text, 0, 0, "Great! Now, what should we call you?")
        name = input_str(0, 0, graphics, 10, "Your name:")
        add_text(text, 0, 0, "So your name is %s!" % name)

        with open("player_info.json", 'w') as fw:
            json.dump({'name': name, 'male': gender}, fw)
    else:
        with open("player_info.json") as fr:
            info = json.load(fr)
        add_text(text, 0, 0, "So your name is %s, and you're a %s!"
                 % (info['name'], 'boy' if info['male'] else 'girl'))

    text.getch()'''

    CGBattle([sysnake, my_prenty], [prenty], graphics, text, choice).start_battle()
    text.getch()


c.wrapper(main)
