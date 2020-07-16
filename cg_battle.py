import curses as c
from funcs import choose, print_text
from cg_moves import *
from settings import base_exp


class CGBattle:
    def __init__(self, player, opponent, graphics_win: c.window,
                 text_win: c.window, choice_win: c.window, is_wild=True):
        self.player = player
        self.my_team = player.team
        self.opponent = opponent
        self.opponent_team = [opponent] if is_wild else opponent.team
        self.graphics: c.window = graphics_win
        self.text: c.window = text_win
        self.choice: c.window = choice_win
        self.my_active, self.opponent_active = self.my_team[0], self.opponent_team[0]
        self.turn_num = 0
        self.is_wild = is_wild
        self.ran = False
        if not is_wild:
            self.opponent_name = opponent.name
        if is_wild and len(self.opponent_team) > 1:
            raise ValueError("More than one wild CGs appearing at once.")

        self.participated = [self.my_active]

    def show_my_cg(self):
        for i, line in enumerate(self.my_active.sprite_back):
            self.graphics.addstr(9 + i, 0, line)
        self.graphics.addstr(6, 1, self.my_active.name)
        self.graphics.addstr(6, 14, "Lv%d" % self.my_active.level)
        my_hp_symbols = int(self.my_active.current_stats[0] * 12 / self.my_active.normal_stats[0]) \
            if self.my_active.current_stats[0] > 0 else 0
        self.graphics.addstr(7, 1, "HP:|%s|" %
                             ('#' * my_hp_symbols + ' ' * (12 - my_hp_symbols)))
        self.graphics.addstr(7, 18, "%d/%d     " %
                             (int(self.my_active.current_stats[0]), self.my_active.normal_stats[0]))
        exp_symbols = int((self.my_active.exp -
                          base_exp[self.my_active.exp_group][self.my_active.level])
                          * 12 / (base_exp[self.my_active.exp_group][self.my_active.level + 1]
                                  - base_exp[self.my_active.exp_group][self.my_active.level]))
        self.graphics.addstr(8, 1, "Exp:%s|" % ('-' * exp_symbols + ' ' * (12 - exp_symbols)))
        self.graphics.refresh()

    def show_opponent_cg(self):
        for i, line in enumerate(self.opponent_active.sprite_front):
            self.graphics.addstr(i, 58, line)
        self.graphics.addstr(8, 59, self.opponent_active.name)
        self.graphics.addstr(8, 72, "Lv%d" % self.opponent_active.level)
        opponent_symbols = int(self.opponent_active.current_stats[0] * 12 /
                               self.opponent_active.normal_stats[0])\
            if self.opponent_active.current_stats[0] > 0 else 0
        self.graphics.addstr(9, 59, "HP:|%s|" %
                             ('#' * opponent_symbols + ' ' *
                              (12 - opponent_symbols)))
        self.graphics.refresh()

    def show_battlers(self):
        for i, line in enumerate(self.player.sprite):
            self.graphics.addstr(9 + i, 0, line)
        for i, line in enumerate(self.opponent.sprite):
            self.graphics.addstr(i, 58, line)
        self.graphics.refresh()

    def refresh_graphics(self):
        if self.ran:
            self.graphics.erase()
            self.graphics.refresh()
        else:
            self.graphics.erase()
            self.show_my_cg()
            self.show_opponent_cg()

    def check(self):
        self.my_active.check()
        if not self.my_active.alive:
            if self.my_active in self.my_team:
                self.my_team.remove(self.my_active)
        self.opponent_active.check()
        if not self.opponent_active.alive:
            self.my_active.gain_exp(1000)
            self.show_my_cg()
            if self.opponent_active in self.opponent_team:
                self.opponent_team.remove(self.opponent_active)

    def exec_turn(self):
        self.refresh_graphics()
        my_action = self.get_my_action()
        opponent_action = self.ai_get_opponent_action()
        if my_action['type'] == 'fight' and opponent_action['type'] == 'fight':
            if self.my_active.current_stats[3] > self.opponent_active.current_stats[3]:
                self.my_active.use_move(self.opponent_active, my_action['arg'])
                self.refresh_graphics()
                self.check()
                if self.opponent_active.alive:
                    self.opponent_active.use_move(self.my_active, opponent_action['arg'])
                    self.refresh_graphics()
                    self.check()
                else:
                    opponent_action = self.ai_get_opponent_action()
                    self.opponent_active = opponent_action['arg']
                    if self.opponent_active:
                        print_text(self.text, "%s sent out %s!" %
                                   (self.opponent_name, self.opponent_active.name))
            else:
                self.opponent_active.use_move(self.my_active, opponent_action['arg'])
                self.refresh_graphics()
                self.check()
                if self.my_active.alive:
                    self.my_active.use_move(self.opponent_active, my_action['arg'])
                    self.refresh_graphics()
                    self.check()
                elif self.my_team:
                    my_action = self.get_my_action()
                    self.my_active = my_action['arg']
                    print_text(self.text, "Go! %s!" % self.my_active.name)
        elif 'fight' == my_action['type']:
            if opponent_action['type'] == 'switch':
                if self.opponent_active.alive:
                    print_text(self.text, "%s withdrew %s!" % (self.opponent_name, self.opponent_active.name))
                self.opponent_active = opponent_action['arg']
                print_text(self.text, "%s sent out %s!" % (self.opponent_name, self.opponent_active.name))
                self.participated = [self.my_active]
                self.refresh_graphics()
                self.my_active.use_move(self.opponent_active, my_action['arg'])
                self.refresh_graphics()
                self.check()
        elif 'fight' == opponent_action['type']:
            if my_action['type'] == 'switch':
                print_text(self.text, "Come back, %s!" % self.my_active.name)
                self.my_active = my_action['arg']
                print_text(self.text, "You're in charge, %s!" % self.my_active.name)
                self.participated.append(self.my_active)
                self.refresh_graphics()
                self.opponent_active.use_move(self.my_active, opponent_action['arg'])
            elif my_action['type'] == 'run':
                if self.is_wild:
                    self.ran = True
                else:
                    print_text(self.text, "There's no running away from a Trainers' battle!")
                    self.opponent_active.use_move(self.my_active, opponent_action['arg'])
            self.refresh_graphics()
            self.check()

        self.turn_num += 1

    def get_my_action(self) -> dict:
        type_map = {'q': 'FIGHT', 'w': 'SWITCH', 'e': 'RUN'}
        final_type = type_map[choose(self.choice, type_map, self.text, "What will %s do?" % self.my_active.name)]\
            .lower() if self.my_active.alive else 'switch'
        arg = None
        if final_type == 'fight':
            move_map = {}
            for i, move in enumerate(self.my_active.move_set):
                move_map[['q', 'w', 'e', 's'][i]] = move
            arg = move_map[choose(self.choice, move_map)]
        elif final_type == 'switch':
            print_text(self.text, "Which CREAGRAM do you wish to switch into?", 0)
            cg_info = {}
            cg_map = {}
            for i, cg in enumerate(self.my_team):
                cg_info[['q', 'w', 'e', 'a', 's', 'd'][i]] =\
                    "%s   Lv%d   HP: %d/%d" % (cg.name, cg.level, int(cg.current_stats[0]), cg.normal_stats[0])
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
                    if isinstance(every_move, CGStatusMove):
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
        c.flash()
        c.napms(150)
        c.flash()
        self.graphics.erase()
        self.graphics.refresh()
        if self.is_wild:
            print_text(self.text, 'A wild %s appeared!' % self.opponent_team[0].name, 0)
        else:
            print_text(self.text, '%s challenged you to a battle!' % self.opponent_name, 0)
            self.show_battlers()
            c.napms(1000)
            print_text(self.text, "%s sent out %s!" % (self.opponent_name, self.opponent_team[0].name), 0)
        self.show_opponent_cg()
        c.napms(1000)
        print_text(self.text, "Go! %s!" % self.my_team[0].name, 0)
        self.show_my_cg()
        c.napms(1000)

        while self.my_team and self.opponent_team and not self.ran:
            self.exec_turn()

        self.text.erase()
        if self.ran:
            print_text(self.text, 'You got away safely!', -1)
        elif self.my_team:
            if self.is_wild:
                pass
            else:
                print_text(self.text, self.opponent.lose_text, -1)
        elif self.opponent_team:
            print_text(self.text, 'You have no usable CREAGRAM\'s left!')
            print_text(self.text, 'You blacked out!', -1)
