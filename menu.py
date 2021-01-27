import curses as c
import curses.panel as cp
from funcs import choose


def start_menu(begin, end, choices, actions):
    menu_win = c.newwin(end[0] - begin[0], end[1] - begin[1], begin[0], begin[1])
    menu_panel = cp.new_panel(menu_win)
    menu_win.border('|', '|', '-', '-', '+', '+', '+', '+')
    menu_win.noutrefresh()
    choices_win = menu_win.derwin(end[0] - begin[0] - 2, end[1] - begin[1] - 2, 1, 1)
    choices['x'] = 'EXIT'
    actions['x'] = lambda: None

    key = choose(choices_win, choices)
    menu_panel.hide()
    actions[key]()


if __name__ == "__main__":
    c.wrapper(lambda scr: start_menu((0, 0), (5, 10), {
        'q': 'ABC',
        'w': 'DEF'
    }, {
        'q': lambda: None,
        'w': lambda: None
    }))
