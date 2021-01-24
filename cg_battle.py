from funcs import *
from cg_moves import *
from settings import exp_yield


class CGBattle:
    def __init__(self, player, opponent, graphics_win: c.window,
                 text_win: c.window, choice_win: c.window, is_wild=True):
        self.player = player
        self.my_team = player.team
        self.opponent = opponent
        self.opponent_team = [opponent] if is_wild else opponent.team

        for cg in self.opponent_team:
            if is_wild:
                cg.is_wild = True
            else:
                cg.is_opponent = True

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

        for cg in self.opponent_team:
            cg.check()

        self.participated = [self.my_active]

    def show_my_cg(self):
        for i, line in enumerate(self.my_active.sprite_back):
            self.graphics.addstr(9 + i, 0, line)
        self.graphics.addstr(6, 1, self.my_active.name)
        self.graphics.addstr(6, 14, "Lv%d" % self.my_active.level)
        self.graphics.addstr(7, 1, get_hp_string(self.my_active))
        self.graphics.addstr(7, 18, "%d/%d     " %
                             (self.my_active.current_hp, self.my_active.normal_hp))
        self.graphics.addstr(8, 1, get_exp_string(self.my_active))
        self.graphics.refresh()

    def show_opponent_cg(self):
        for i, line in enumerate(self.opponent_active.sprite_front):
            self.graphics.addstr(i, 58, line)
        self.graphics.addstr(8, 59, self.opponent_active.name)
        self.graphics.addstr(8, 72, "Lv%d" % self.opponent_active.level)
        self.graphics.addstr(9, 59, get_hp_string(self.opponent_active))
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
            if self.my_active.level == self.opponent_active.level:
                delta_exp = exp_yield[self.opponent_active.name]\
                            * (1 if self.is_wild else 1.5) * self.my_active.level // 7
            else:
                delta_exp = exp_yield[self.opponent_active.name]\
                            * (1 if self.is_wild else 1.5) * self.opponent_active.level / 5
                delta_exp *= ((2 * self.opponent_active.level + 10) /
                              (self.my_active.level + self.opponent_active.level + 10)) ** 2.5
                delta_exp += 1

            delta_exp /= len(self.participated)
            delta_exp = int(delta_exp)
            for cg in self.participated:
                cg.gain_exp(delta_exp)
            self.show_my_cg()
            if self.opponent_active in self.opponent_team:
                self.opponent_team.remove(self.opponent_active)

    def exec_turn(self):
        self.refresh_graphics()
        my_action = self.get_my_action()
        opponent_action = self.ai_get_opponent_action()
        if my_action['type'] == 'fight' and opponent_action['type'] == 'fight':
            if self.my_active.current_stats[2] > self.opponent_active.current_stats[2]:
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
                    self.opponent_active.current_stats = self.opponent_active.normal_stats[:]
                    self.opponent_active.stat_stages = [0] * 3
                self.opponent_active = opponent_action['arg']
                print_text(self.text, "%s sent out %s!" % (self.opponent_name, self.opponent_active.name))
                self.refresh_graphics()
                self.my_active.use_move(self.opponent_active, my_action['arg'])
                self.refresh_graphics()
                self.check()
        elif 'fight' == opponent_action['type']:
            if my_action['type'] == 'switch':
                print_text(self.text, "Come back, %s!" % self.my_active.name)
                self.my_active.current_stats = self.my_active.normal_stats[:]
                self.my_active.stat_stages = [0] * 3
                self.my_active = my_action['arg']
                print_text(self.text, "You're in charge, %s!" % self.my_active.name)
                if self.my_active not in self.participated:
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
            while True:
                cg = choose_cg(self.graphics, self.my_team, self.text, "Which CREAGRAM do you wish to switch into?")
                action = choose(self.choice, {'q': "SUMMARY", 'w': "SWITCH IN", 'e': "CANCEL"},
                                self.text, "What do you wish to do with %s?" % cg.name)
                if action == 'q':
                    cg_summary(self.graphics, cg)
                    print_text(self.text, "Press any key to return...", 0)
                    self.graphics.getch()
                elif action == 'w':
                    arg = cg
                    break

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
            print_text(self.text, 'You got away safely!', 0)
        elif self.my_team:
            if not self.is_wild:
                print_text(self.text, self.opponent.lose_text, 0)
        elif self.opponent_team:
            print_text(self.text, 'You have no usable CREAGRAM\'s left!')
            print_text(self.text, 'You blacked out!', 0)

        self.my_active.current_stats = self.my_active.normal_stats[:]
        self.my_active.stat_stages = [0] * 3

        self.graphics.erase()
        self.text.erase()
