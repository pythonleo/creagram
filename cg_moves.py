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


class CGStatMove(CGMove):
    def __init__(self, stat, factor: float, name, affect_self=False):
        super().__init__(name)
        self.stat = stat
        self.factor = factor
        self.affect_self = affect_self

    def use(self, user, opponent):
        exec("%s.%s *= %f" % ('user' if self.affect_self else 'opponent', self.stat, self.factor))
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
            opponent.current_hp -= eff * self.power * user.attack / opponent.defense
            return eff
        else:
            return -1


hazard = CGDmgMove(30, 1, env, "HAZARD")
skill_attack = CGDmgMove(30, 1, skill, "SKILL ATTACK")
viral_wave = CGDmgMove(30, 1, virus, "VIRAL WAVE")
lock_throw = CGDmgMove(30, 1, secure, "LOCK THROW")
glitch = CGDmgMove(30, 1, bug, "GLITCH")

weakest = CGDmgMove(0, 0, env, '')

defense_break = CGStatMove('defense', .75, "DEFENSE BREAK")
display_code = CGStatMove('attack', .5, "DISPLAY CODE")
