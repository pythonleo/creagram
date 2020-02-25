class CGType:
    def __init__(self, weak=None, resist=None, immune=None):
        self.weak = weak
        self.resist = resist
        self.immune = immune

    def calc_effectiveness(self, foe):
        if self.weak == foe:
            return 2
        elif self.resist == foe:
            return .5
        elif self.immune == foe:
            return 0
        else:
            return 1


env = CGType()
virus = CGType()
secure = CGType()
bug = CGType()
skill = CGType()
env.weak, env.resist, env.immune = secure, bug, skill
virus.weak, virus.resist, virus.immune = bug, skill, env
secure.weak, secure.resist, secure.immune = skill, env, virus
bug.weak, bug.resist, bug.immune = env, virus, secure
skill.weak, skill.resist, skill.immune = virus, secure, bug
