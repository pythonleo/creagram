from cg_types import *
from random import random as r


class CGMove:
    def __init__(self, name):
        self.name = name
        self.__str__ = self.__repr__

    def __repr__(self):
        return self.name

    def use(self, user, opponent) -> float:
        pass


class CGStatusMove(CGMove):
    def __init__(self, stat, increment_stage: int, name, affect_self=False):
        super().__init__(name)
        self.stat = stat
        self.increment_stage = increment_stage
        self.affect_self = affect_self

    def use(self, user, opponent):
        affected = user if self.affect_self else opponent
        if abs(affected.stat_stages[self.stat] + self.increment_stage) > 6:
            return -3 if self.increment_stage > 0 else -4
        exec("%s.stat_stages[%d] += %d" %
             ('user' if self.affect_self else 'opponent', self.stat, self.increment_stage))
        return -2


class CGDmgMove(CGMove):
    def __init__(self, power, accuracy, move_type, name):
        super().__init__(name)
        self.power = power
        self.accuracy = accuracy
        self.type = move_type

    def use(self, user, opponent):
        if r() <= self.accuracy:
            eff = opponent.calc_effectiveness(self.type)
            opponent.current_stats[0] -= int((self.power * user.current_stats[1] /
                                          opponent.current_stats[2] *
                                          ((2 / 5 * user.level + 2) + 2) / 50) * eff)
            if(opponent.current_stats[0] < 0):
                opponent.current_stats[0] = 0
            return eff
        else:
            return -1


hazard = CGDmgMove(30, 1, env, "HAZARD")
skill_attack = CGDmgMove(30, 1, skill, "SKILL ATTACK")
viral_wave = CGDmgMove(30, 1, virus, "VIRAL WAVE")
lock_throw = CGDmgMove(30, 1, secure, "LOCK THROW")
glitch = CGDmgMove(30, 1, bug, "GLITCH")

weakest = CGDmgMove(0, 0, env, '')

defense_break = CGStatusMove(1, -1, "DEFENSE BREAK")
display_code = CGStatusMove(0, -2, "DISPLAY CODE")
