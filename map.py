from map_obj import *
from funcs import *
from settings import default_player_pos, menu_items, menu_actions


def start_map(gfx, text, choice, top_lf, btm_rt, size, objects, player):
    main_map = area = Map(size[0], size[1], objects)

    y_now, x_now = 0, 0

    forbidden = {}
    step_event = {}
    doors = {}
    triggers = {}
    for o in main_map.obj:
        if o.block:
            for y in range(o.start_y, o.start_y + len(o.string_shown.split('\n'))):
                for x in range(o.start_x, o.start_x + len(o.string_shown.split('\n')[0])):
                    if o.door and (y - o.start_y, x - o.start_x) == o.door['pos']:
                        doors[(y, x)] = (o.door['map'], o.door['exit'], o.door['transport'],
                                         (o.door['pos'][0] + o.start_y + 1, o.door['pos'][1] + o.start_x))
                    else:
                        forbidden[(y, x)] = o

                    if isinstance(o, Interactive) and o.detect:
                        is_x = o.detect[0] == 'x'
                        main_axis = eval("o.start_%s" % o.detect[0])
                        other_axis = eval("o.start_%s" % {'x': 'y', 'y': 'x'}[o.detect[0]])
                        for i in range(main_axis, main_axis + o.detect[1]):
                            triggers[(other_axis, i) if is_x else (i, other_axis)] = o
        elif isinstance(o, Interactive):
            for y in range(o.start_y, o.start_y + len(o.string_shown.split('\n')) - 1):
                for x in range(o.start_x, o.start_x + len(o.string_shown.split('\n')[0])):
                    step_event[(y, x)] = o
    main_map.pd.erase()
    for o in main_map.obj:
        for i, line in enumerate(o.string_shown.split('\n')):
            main_map.pd.addstr(o.start_y + i, o.start_x, line)
    main_map.pd.addstr(player.start_y, player.start_x, player.string_shown)
    main_map.pd.refresh(y_now, x_now, top_lf[0], top_lf[1], btm_rt[0], btm_rt[1])

    def check_trigger():
        if (player.start_y, player.start_x) in triggers:
            triggers[(player.start_y, player.start_x)]\
                .on_interacted_with(player, gfx, text, choice)
        elif (player.start_y, player.start_x) in step_event:
            step_event[(player.start_y, player.start_x)]\
                .on_interacted_with(player, gfx, text, choice)

    def refresh_map():
        main_map.pd.erase()
        for map_obj in main_map.obj:
            for line_num, line_content in enumerate(map_obj.string_shown.split('\n')):
                main_map.pd.addstr(map_obj.start_y + line_num, map_obj.start_x, line_content)
        main_map.pd.addstr(player.start_y, player.start_x, player.string_shown)
        main_map.pd.refresh(y_now, x_now, top_lf[0], top_lf[1], btm_rt[0], btm_rt[1])

    looking_at = None
    while True:
        refresh_map()
        gfx.refresh()
        ch = gfx.getch()
        if ch in (c.KEY_UP, 450):
            if y_now > 0 and (player.start_y - 1, player.start_x) not in forbidden:
                y_now -= 1
                refresh_map()
                check_trigger()
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
                refresh_map()
                check_trigger()
            if player.start_y < main_map.height - 2:
                if (player.start_y + 1, player.start_x) in forbidden:
                    looking_at = forbidden[(player.start_y + 1, player.start_x)]
                else:
                    looking_at = None
                    player.start_y += 1
        elif ch in (c.KEY_LEFT, 452):
            if x_now > 0 and (player.start_y, player.start_x - 1) not in forbidden:
                x_now -= 1
                refresh_map()
                check_trigger()
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
                refresh_map()
                check_trigger()
            if player.start_x < main_map.width - 2:
                if (player.start_y, player.start_x + 1) in forbidden:
                    looking_at = forbidden[(player.start_y, player.start_x + 1)]
                else:
                    looking_at = None
                    player.start_x += 1
        elif ch in (c.KEY_ENTER, 10):
            if isinstance(looking_at, Interactive):
                looking_at.on_interacted_with(player, gfx, text, choice)
        elif ch == ord('x'):
            ch = choose(choice, menu_items)
            exec(menu_actions[ch])
        elif ch == ord('q'):
            raise ValueError('exit')

        if (player.start_y, player.start_x) in doors:
            to_go = doors[(player.start_y, player.start_x)]
            main_map = to_go[0]
            player.start_y, player.start_x = to_go[2]
            y_now, x_now = 0, 0
            gfx.erase()
            forbidden = {}
            doors = {(to_go[1]): (area, None, to_go[3], None)}
            for o in main_map.obj:
                if o.block:
                    for y in range(o.start_y, o.start_y + len(o.string_shown.split('\n'))):
                        for x in range(o.start_x, o.start_x + len(o.string_shown.split('\n')[0])):
                            if o.door and (y - o.start_y, x - o.start_x) == o.door['pos']:
                                doors[(y, x)] = (o.door['map'], o.door['exit'], o.door['transport'],
                                                 (o.door['pos'][0] + o.start_y + 1,
                                                  o.door['pos'][1] + o.start_x))
                            else:
                                forbidden[(y, x)] = o

        triggers = {}
        for o in main_map.obj:
            if isinstance(o, Interactive) and o.detect:
                is_x = o.detect[0] == 'x'
                main_axis = eval("o.start_%s" % o.detect[0])
                other_axis = eval("o.start_%s" % {'x': 'y', 'y': 'x'}[o.detect[0]])
                for i in range(main_axis, main_axis + o.detect[1]):
                    triggers[(other_axis, i) if is_x else (i, other_axis)] = o
