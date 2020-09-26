import curses as c


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


def choose(scr: c.window, choices: dict, *args):
    if args:
        print_text(args[0], args[1], False)
    scr.erase()
    for i, key in enumerate(choices):
        scr.addstr(i, 0, "%s: %s" % (key.upper(), choices[key]))
    while True:
        key = scr.getkey()
        if key in choices.keys():
            scr.erase()
            return key


def print_text(text, str_to_print, pause: int = 1):
    text.erase()
    for i, ch in enumerate(str_to_print):
        text.addch(0, i, ch)
        c.napms(40)
    if pause == 1:
        c.napms(1000)
    elif pause == -1:
        text.getch()


def show_team(gfx: c.window, team: list):
    for i, cg in enumerate(team):
        symbols = int(cg.current_stats[0] * 12 / cg.normal_stats[0]) \
            if cg.current_stats[0] > 0 else 0
        gfx.addstr(3 * i, 1, "%s Lv%d HP:|%s| %d/%d Atk %d Def %d Spe %d" %
                   (cg.name, cg.level, '#' * symbols + ' ' * (12 - symbols),
                    cg.current_stats[0], cg.normal_stats[0],
                    cg.current_stats[1], cg.current_stats[2], cg.current_stats[3]))
