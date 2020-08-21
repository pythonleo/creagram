from map_obj import *
from funcs import *
from settings import default_player_pos


def start_map(gfx, text, choice, top_lf, btm_rt, size, objects, player):
    main_map = area = Map(size[0], size[1], objects)

    y_now, x_now = 0, 0

    forbidden = {}
    doors = {}
    for o in main_map.obj:
        if o.block:
            for y in range(o.start_y, o.start_y + len(o.string_shown.split('\n'))):
                for x in range(o.start_x, o.start_x + len(o.string_shown.split('\n')[0])):
                    if o.door and (y - o.start_y, x - o.start_x) == o.door['pos']:
                        doors[(y, x)] = (o.door['map'], o.door['exit'])
                    else:
                        forbidden[(y, x)] = o

    looking_at = None
    while True:
        main_map.pd.erase()
        for o in main_map.obj:
            for i, line in enumerate(o.string_shown.split('\n')):
                main_map.pd.addstr(o.start_y + i, o.start_x, line)
        main_map.pd.addstr(player.start_y, player.start_x, player.string_shown)
        main_map.pd.refresh(y_now, x_now, top_lf[0], top_lf[1], btm_rt[0], btm_rt[1])
        gfx.refresh()
        ch = gfx.getch()
        if ch in (c.KEY_UP, 450):
            if y_now > 0 and (player.start_y - 1, player.start_x) not in forbidden:
                y_now -= 1
            if player.start_y > 0:
                if (player.start_y - 1, player.start_x) in forbidden:
                    looking_at = forbidden[(player.start_y - 1, player.start_x)]
                else:
                    looking_at = None
                    player.start_y -= 1
        elif ch in (c.KEY_DOWN, 456):
            if default_player_pos[0] <= player.start_y < main_map.height - 2\
                    and (player.start_y + 1, player.start_x) not in forbidden:
                y_now += 1
            if player.start_y < main_map.height - 2:
                if (player.start_y + 1, player.start_x) in forbidden:
                    looking_at = forbidden[(player.start_y + 1, player.start_x)]
                else:
                    looking_at = None
                    player.start_y += 1
        elif ch in (c.KEY_LEFT, 452):
            if x_now > 0 and (player.start_y, player.start_x - 1) not in forbidden:
                x_now -= 1
            if player.start_x > 0:
                if (player.start_y, player.start_x - 1) in forbidden:
                    looking_at = forbidden[(player.start_y, player.start_x - 1)]
                else:
                    looking_at = None
                    player.start_x -= 1
        elif ch in (c.KEY_RIGHT, 454):
            if default_player_pos[1] <= player.start_x < main_map.width - 2\
                    and (player.start_y, player.start_x + 1) not in forbidden:
                x_now += 1
            if player.start_x < main_map.width - 2:
                if (player.start_y, player.start_x + 1) in forbidden:
                    looking_at = forbidden[(player.start_y, player.start_x + 1)]
                else:
                    looking_at = None
                    player.start_x += 1
        elif ch in (c.KEY_ENTER, 10):
            if isinstance(looking_at, Interactive):
                looking_at.on_interacted_with(player, gfx, text, choice)
        elif ch == ord('q'):
            raise ValueError('exit')

        if (player.start_y, player.start_x) in doors:
            to_go = doors[(player.start_y, player.start_x)]
            main_map = to_go[0]
            gfx.erase()
            forbidden = []
            doors = {(to_go[1]): (area, None)}
            for o in main_map.obj:
                if o.block:
                    for y in range(o.start_y, o.start_y + len(o.string_shown.split('\n'))):
                        for x in range(o.start_x, o.start_x + len(o.string_shown.split('\n')[0])):
                            if o.door and (y - o.start_y, x - o.start_x) == o.door['pos']:
                                doors[(y, x)] = (o.door['map'], o.door['exit'])
                            else:
                                forbidden.append((y, x))
