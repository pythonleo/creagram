import curses as c
from settings import base_exp


def init_borders(scr):
    scr.border('|', '|', '-', '-', '+', '+', '+', '+')
    scr.addstr(18, 0, '+' + '-' * 52 + '+' + '-' * 25 + '+')
    for i in range(4):
        scr.addch(19 + i, 53, '|')
    scr.addch(23, 53, '+')
    scr.refresh()


def show_sprite(scr: c.window, sprite: list, erase=True):
    if erase:
        scr.erase()
    scr_y, scr_x = scr.getmaxyx()
    begin_y = scr_y // 2 - len(sprite) // 2
    begin_x = scr_x // 2 - len(sprite[0]) // 2

    for i, s in enumerate(sprite):
        scr.addstr(begin_y + i, begin_x, s)
    scr.refresh()


def sprite_init(scr: c.window, text: c.window, sprite: dict, erase=True):
    show_sprite(scr, sprite['image'], erase)
    for group in sprite['lines']:
        for i, line in enumerate(group):
            text.addstr(i, 0, line)
        text.getch()
        text.erase()
    scr.erase()
    scr.refresh()


def input_str(y, x, scr: c.window, max_len=0, prompt=''):
    res = ''
    len_count = 0
    if prompt:
        scr.addstr(y, x, prompt)
    if max_len > 0:
        scr.addstr(y + int(bool(prompt)), x, '_' * max_len)
    while True:
        char = scr.get_wch()
        if char == '\n':
            break
        elif char in ('\b', '\x7f'):
            if len_count > 0:
                res = res[:-1]
                scr.addch(y + int(bool(prompt)), x + len_count - 1, '_')
                scr.refresh()
                len_count -= 1
                
        elif len(char) == 1:
            res += char
            scr.addch(y + int(bool(prompt)), x + len_count, char)
            scr.refresh()
            len_count += 1

        if 0 < max_len <= len_count:
            break

    return res


def choose(scr, choices: dict, *args):
    if args:
        print_text(args[0], args[1], False)
    scr.erase()

    line_num = 0
    for key in choices:
        scr.addstr(line_num, 0, "%s: " % key.upper())
        for line in str(choices[key]).split('\n'):
            scr.addstr(line_num, 3, line)
            line_num += 1

    while True:
        key = scr.getkey()
        if key in choices.keys():
            scr.erase()
            return key


def print_text(text, str_to_print, pause: int = 1):
    text.erase()
    line = 0
    for i, ch in enumerate(str_to_print):
        if ch == '\n':
            line += 1
        else:
            text.addch(line, i, ch)
            c.napms(40)
    if pause == 1:
        c.napms(1000)
    elif pause == -1:
        text.getch()


def choose_cg(gfx, team: list, prompt_win=None, prompt_text=None):
    keys = ['q', 'w', 'e', 'a', 's', 'd']
    choices = {}
    key_to_cg = {'x': None}
    for i, cg in enumerate(team):
        choices[keys[i]] = ("%s Lv%d %s %d/%d Atk %d Def %d Spe %d" %
                            (cg.name, cg.level, get_hp_string(cg),
                             cg.current_hp, cg.normal_hp,
                             cg.current_stats[0],
                             cg.current_stats[1],
                             cg.current_stats[2]))
        key_to_cg[keys[i]] = cg
    choices['x'] = 'Exit'

    if prompt_win and prompt_text:
        key = choose(gfx, choices, prompt_win, prompt_text)
    else:
        key = choose(gfx, choices)

    chosen_cg = key_to_cg[key]
    return chosen_cg


def get_hp_string(cg):
    hp_symbols = int(cg.current_hp * 12 / cg.normal_hp) \
        if cg.current_hp > 0 else 0
    return "HP:|%s|" % ('#' * hp_symbols + ' ' * (12 - hp_symbols))


def get_exp_string(cg):
    if cg.level == 100:
        return ''
    exp_symbols = int((cg.exp - base_exp[cg.exp_group][cg.level - 1])
                      * 12 / (base_exp[cg.exp_group][cg.level]
                              - base_exp[cg.exp_group][cg.level - 1]))
    return "EXP:%s|" % ('-' * exp_symbols + ' ' * (12 - exp_symbols))


def cg_summary(gfx, cg):
    gfx.erase()

    # sprite
    for i, line in enumerate(cg.sprite_front):
        gfx.addstr(i + 1, 1, line)

    # basic info (name, types, level)
    gfx.addstr(1, 27, "Name: %s (%s)" % (cg.name, cg.species))
    gfx.addstr(1, 65, "Lv. %d" % cg.level)
    gfx.addstr(2, 27, "Typing: %s%s" % (
        cg.types[0].name, '' if len(cg.types) == 1 else '/' + cg.types[1].name
    ))

    # HP
    gfx.addstr(4, 27, get_hp_string(cg))
    gfx.addstr(4, 45, "%d/%d" % (cg.current_hp, cg.normal_hp))

    # EXP
    if cg.level < 100:
        gfx.addstr(6, 27, get_exp_string(cg))
        gfx.addstr(6, 45, "To next level: %d" % (base_exp[cg.exp_group][cg.level] - cg.exp))

    # other stats
    gfx.addstr(8, 27, "Attack %d      Defense %d      Speed %d" % (
        cg.normal_stats[0], cg.normal_stats[1], cg.normal_stats[2]
    ))

    # moves
    display_y = [11, 11, 13, 13]
    display_x = [4, 42, 4, 42]
    for i, move in enumerate(cg.move_set):
        gfx.addstr(display_y[i], display_x[i], "%s (%s)" % (
            move.name, move.type.name if move.typed else "STATUS"
        ))

    gfx.refresh()


def cg_menu(graphics, text, player):
    while True:
        cg = choose_cg(graphics, player.team, text, "Choose a CREAGRAM in order to see its SUMMARY.")
        if not cg:
            break
        cg_summary(graphics, cg)
        print_text(text, 'Press any key to return...', -1)

    text.erase()


def capitalize(a: str):
    return a[0].upper() + a[1:]
