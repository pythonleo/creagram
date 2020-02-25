from cg_moves import *
from cg_sprites import *
from errors import *
from curses import napms


def sleep(s):
    napms(1000 * s)


class Creagram:
    def __init__(self, sprite_front, sprite_back, name, hp, attack, defense,
                 speed, move_set, types, level=1, status_win=None):
        self.sprite_front = sprite_front
        self.sprite_back = sprite_back
        self.name = name
        self.full_hp = self.current_hp = hp + level * 3
        self.attack = attack + level * 3
        self.defense = defense + level * 3
        self.speed = speed + level * 2
        self.move_set = move_set
        self.types = types
        self.level = level
        self.status_win = status_win
        self.alive = True

    def calc_effectiveness(self, opponent_type):
        res = 1
        for my_type in self.types:
            res *= my_type.calc_effectiveness(opponent_type)

        return res

    def use_move(self, opponent, move):
        if move in self.move_set:
            if self.alive:
                self.status_win.erase()
                self.status_win.addstr(0, 0, "%s used %s!" % (self.name, move.name))
                self.status_win.refresh()
                sleep(1)
                status_code = move.use(self, opponent)
                self.status_win.erase()
                if status_code > 1:
                    self.status_win.addstr(0, 0, "It's super effective!")
                elif 0 < status_code < 1:
                    self.status_win.addstr(0, 0, "It's not very effective...")
                elif status_code == 0:
                    self.status_win.addstr(0, 0, "It doesn't affect %s..." % opponent.name)
                elif status_code == -1:
                    self.status_win.addstr(0, 0, "But it missed!")
                elif status_code == -2:
                    self.status_win.addstr(0, 0, "%s's %s %s!" % (
                        self.name if move.affect_self else opponent.name,
                        move.stat, 'fell' if move.factor < 1 else 'rose'
                    ))
                self.status_win.refresh()
                sleep(1)
        else:
            raise InvalidMoveError("Move not in user's move set.")

    def check(self):
        if self.current_hp <= 0:
            self.faint()

    def faint(self):
        self.status_win.erase()
        self.status_win.addstr(0, 0, "%s fainted!" % self.name)
        self.status_win.refresh()
        sleep(1)
        self.alive = False


class Sysnake(Creagram):
    def __init__(self, status_win, level, name="SYSNAKE"):
        super().__init__(sysnake_sprite_front, sysnake_sprite_back, name, 60, 30, 15, 40,
                         [hazard, defense_break], [env], level, status_win)


class Prenty(Creagram):
    def __init__(self, status_win, level, name="PRENTY"):
        super().__init__(prenty_sprite_front, prenty_sprite_back, name, 55, 23, 30, 44,
                         [skill_attack, display_code], [skill], level, status_win)
