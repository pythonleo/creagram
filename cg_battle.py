import curses as c
from funcs import choose
from cg_moves import *
from errors import *
from curses import napms


def sleep(s):
    napms(1000 * s)


class CGBattle:
    def __init__(self, my_team, opponent_team, graphics_win: c.window,
                 text_win: c.window, choice_win: c.window, opponent_name=None, is_wild=True):
        self.my_team = my_team
        self.opponent_team = opponent_team
        self.graphics: c.window = graphics_win
        self.text: c.window = text_win
        self.choice: c.window = choice_win
        self.my_active, self.opponent_active = self.my_team[0], self.opponent_team[0]
        self.turn_num = 0
        self.is_wild = is_wild
        self.ran = False
        if not is_wild:
            self.opponent_name = opponent_name
        if is_wild and len(opponent_team) > 1:
            raise WildBattleError("More than one wild CGs appearing at once.")

    def print(self, str_to_print):
        self.text.erase()
        self.text.addstr(0, 0, str_to_print)
        self.text.refresh()
        sleep(1)

    def refresh_graphics(self):
        if self.ran:
            self.graphics.erase()
            self.graphics.refresh()
        else:
            for i, line in enumerate(self.my_active.sprite_back):
                self.graphics.addstr(9 + i, 0, line)
            self.graphics.addstr(6, 1, self.my_active.name)
            self.graphics.addstr(6, 14, "Lv%d" % self.my_active.level)
            my_symbols = int(self.my_active.current_hp * 12 / self.my_active.full_hp) \
                if self.my_active.current_hp > 0 else 0
            self.graphics.addstr(7, 1, "HP:|%s|" %
                                 ('#' * my_symbols + ' ' * (12 - my_symbols)))
            self.graphics.addstr(8, 6, "%d/%d     " % (int(self.my_active.current_hp), self.my_active.full_hp))
            for i, line in enumerate(self.opponent_active.sprite_front):
                self.graphics.addstr(i, 58, line)
            self.graphics.addstr(8, 59, self.opponent_active.name)
            self.graphics.addstr(8, 72, "Lv%d" % self.opponent_active.level)
            opponent_symbols = int(self.opponent_active.current_hp * 12 / self.opponent_active.full_hp) \
                if self.opponent_active.current_hp > 0 else 0
            self.graphics.addstr(9, 59, "HP:|%s|" %
                                 ('#' * opponent_symbols + ' ' * (12 - opponent_symbols)))
            self.graphics.refresh()

    def check(self):
        self.my_active.check()
        if not self.my_active.alive:
            if self.my_active in self.my_team:
                self.my_team.remove(self.my_active)
        self.opponent_active.check()
        if not self.opponent_active.alive:
            if self.opponent_active in self.opponent_team:
                self.opponent_team.remove(self.opponent_active)

    def exec_turn(self):
        self.refresh_graphics()
        my_action = self.get_my_action()
        opponent_action = self.ai_get_opponent_action()
        if my_action['type'] == 'fight' and opponent_action['type'] == 'fight':
            if self.my_active.speed > self.opponent_active.speed:
                self.my_active.use_move(self.opponent_active, my_action['arg'])
                self.refresh_graphics()
                self.check()
                self.opponent_active.use_move(self.my_active, opponent_action['arg'])
                self.refresh_graphics()
                self.check()
            else:
                self.opponent_active.use_move(self.my_active, opponent_action['arg'])
                self.refresh_graphics()
                self.check()
                self.my_active.use_move(self.opponent_active, my_action['arg'])
                self.refresh_graphics()
                self.check()
        elif 'fight' == my_action['type']:
            self.print("%s withdrew %s!" % (self.opponent_name, self.opponent_active.name))
            self.opponent_active = opponent_action['arg']
            self.print("%s sent out %s!" % (self.opponent_name, self.opponent_active.name))
            self.refresh_graphics()
            self.my_active.use_move(self.opponent_active, my_action['arg'])
            self.refresh_graphics()
            self.check()
        elif 'fight' == opponent_action['type']:
            if my_action['type'] == 'switch':
                self.print("Come back, %s!" % self.my_active.name)
                self.my_active = my_action['arg']
                self.print("You're in charge, %s!" % self.my_active.name)
                self.refresh_graphics()
                self.opponent_active.use_move(self.my_active, opponent_action['arg'])
            elif my_action['type'] == 'run':
                if self.is_wild:
                    self.ran = True
                else:
                    self.print("You can't get away!")
                    self.opponent_active.use_move(self.my_active, opponent_action['arg'])
            self.refresh_graphics()
            self.check()

        self.turn_num += 1

    def get_my_action(self) -> dict:
        self.text.erase()
        self.text.addstr(0, 0, "What will %s do?" % self.my_active.name)
        self.text.refresh()
        type_map = {'q': 'FIGHT', 'w': 'SWITCH', 'e': 'RUN'}
        final_type = type_map[choose(self.choice, type_map)].lower()
        arg = None
        if final_type == 'fight':
            move_map = {}
            for i, move in enumerate(self.my_active.move_set):
                move_map[['q', 'w', 'e', 's'][i]] = move
            arg = move_map[choose(self.choice, move_map)]
        elif final_type == 'switch':
            cg_info = {}
            cg_map = {}
            for i, cg in enumerate(self.my_team):
                cg_info[['q', 'w', 'e', 'a', 's', 'd'][i]] =\
                    "%s   Lv%d   HP: %d/%d" % (cg.name, cg.level, int(cg.current_hp), cg.full_hp)
                cg_map[['q', 'w', 'e', 'a', 's', 'd'][i]] = cg
            arg = cg_map[choose(self.graphics, cg_info)]

        return {'type': final_type, 'arg': arg}

    def ai_get_opponent_action(self) -> dict:
        final_type = ''
        arg = None
        move = weakest
        if self.opponent_active.alive:
            final_type = 'fight'
            if self.turn_num == 0:
                for every_move in self.opponent_active.move_set:
                    if isinstance(every_move, CGStatMove):
                        move = every_move
                        break
                if not move:
                    move = self.opponent_active.move_set[0]
            else:
                for every_move in self.opponent_active.move_set:
                    if isinstance(every_move, CGDmgMove):
                        this_pwr = every_move.power * \
                                   self.my_active.calc_effectiveness(every_move.type)
                        comp_power = move.power * self.my_active.calc_effectiveness(move.type)
                        if this_pwr >= comp_power:
                            move = every_move

            arg = move

        elif self.opponent_team:
            final_type = 'switch'
            arg = self.opponent_team[0]

        return {'type': final_type, 'arg': arg}

    def start_battle(self):
        while self.my_team and self.opponent_team and not self.ran:
            self.exec_turn()

        self.text.erase()
        if self.ran:
            self.text.addstr(0, 0, 'You got away safely!')
        elif self.my_team:
            self.text.addstr(0, 0, 'You won the battle!')
        elif self.opponent_team:
            self.text.addstr(0, 0, 'You lost the battle...')
