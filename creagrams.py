from cg_moves import *
from cg_sprites import *
from funcs import print_text
from curses import napms
from settings import *


def sleep(s):
    napms(1000 * s)


class Creagram:
    """
    The base class for all CGs.
    Should never be initialized on its own.
    """

    species = ''
    exp_group = None

    def __init__(self, sprite_front, sprite_back, name, base_stats,
                 move_set, types, level=1, status_win=None):
        self.sprite_front = sprite_front
        self.sprite_back = sprite_back
        self.name = name

        # All stats are in the format of [HP, Atk, Def, Spe]
        # except for `stat_stages` which is [Atk, Def, Spe]
        self.normal_stats = [base_stats[0] * level // 50 + level + 10] +\
                            [int(base_stats[i] * level // 50 + 5) for i in range(1, 4)]
        self.current_stats = self.normal_stats[:]
        self.stat_stages = [0] * 3

        self.move_set = move_set
        self.types = types
        self.level = level
        self.status_win = status_win
        self.alive = True

        self.exp = base_exp[self.exp_group][self.level]

    def calc_effectiveness(self, opponent_type):
        """Calculates the effectiveness of a move hitting this CG."""
        res = 1
        for my_type in self.types:
            res *= my_type.calc_effectiveness(opponent_type)

        return res

    def gain_exp(self, exp):
        """Gives the CG experience points."""
        print_text(self.status_win,
                   "%s gained %d Exp. Points!" % (self.name, exp))
        self.exp += exp
        while self.exp >= base_exp[self.exp_group][self.level + 1]:
            print_text(self.status_win,
                       "%s grew to Lv. %d!" % (self.name, self.level + 1))
            self.level += 1

    def use_move(self, opponent, move):
        """Use a move on an opponent"""
        if move in self.move_set:
            if self.alive:
                print_text(self.status_win, "%s used %s!" % (self.name, move.name))
                status_code = move.use(self, opponent)
                self.status_win.erase()

                # `status_code` meanings:
                # For a damaging move: its effectiveness or -1 when missing
                # For a status move:
                # -2 when executed successfully
                # -3 when stat is too high
                # -4 when stat is too low
                if status_code > 1:
                    print_text(self.status_win, "It's super effective!")
                elif 0 < status_code < 1:
                    print_text(self.status_win, "It's not very effective...")
                elif status_code == 0:
                    print_text(self.status_win, "It doesn't affect %s..." % opponent.name)
                elif status_code == -1:
                    print_text(self.status_win, "But it missed!")
                elif status_code <= -2:
                    stat_name = {0: 'Attack', 1: "Defense", 2: "Speed"}[move.stat]
                    change = {-3: "severely fell", -2: "harshly fell", -1: "fell",
                              1: "rose", 2: "rose sharply", 3: "rose drastically"}[move.increment_stage]\
                        if status_code == -2 else {-3: "won't go any higher", -4: "won't go any lower"}[status_code]
                    print_text(self.status_win, "%s's %s %s!" % (
                        self.name if move.affect_self else opponent.name, stat_name, change
                    ))
        else:
            raise ValueError("Move not in user's move set.")

    def check(self):
        """
        Check this CG's current state & make changes when necessary.
        Called after every move.
        """
        if self.current_stats[0] <= 0:
            print_text(self.status_win, "%s fainted!" % self.name)
            self.alive = False
        else:
            for stat, stage in enumerate(self.stat_stages):
                self.current_stats[stat+1] = self.normal_stats[stat+1] * stat_multipliers[stage]


class Sysnake(Creagram):
    """For having a correct Python installation in the system."""

    species = 'SYSNAKE'
    exp_group = 'slow'

    def __init__(self, status_win, level, name="SYSNAKE"):
        super().__init__(sysnake_sprite_front, sysnake_sprite_back, name, [53, 50, 28, 40],
                         [hazard, defense_break], [env], level, status_win)


class Prenty(Creagram):
    """For being able to print."""

    species = 'PRENTY'
    exp_group = 'slow'

    def __init__(self, status_win, level, name="PRENTY"):
        super().__init__(prenty_sprite_front, prenty_sprite_back, name, [55, 38, 30, 35],
                         [skill_attack, display_code], [skill], level, status_win)
