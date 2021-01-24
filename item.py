from funcs import print_text


class Item:
    def __init__(self, name, description, player):
        self.name = name
        self.description = description
        self.player = player

    def on_used(self, cg):
        del self.player.bag[self.player.bag.index(self)]

    def held_effect(self, cg):
        pass


class Potion(Item):
    def __init__(self):
        super().__init__('Potion', 'Heals a CREAGRAM\'s health by a little amount.')

    def on_used(self, cg):
        if cg.current_hp == cg.normal_hp:
            print("It won't have any effect.")
            return
        hp_before = cg.current_hp
        cg.current_hp = max(cg.current_hp + 20, cg.normal_hp)
        print_text(cg.status_win, "%s's HP was healed by %d." % (cg.name, cg.current_hp - hp_before), 0)
        super().on_used(cg)
