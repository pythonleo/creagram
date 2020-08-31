import curses as c
from random import random, choice as rand_choice

from cg_battle import CGBattle
from funcs import print_text
from trainer_sprites import player_battle_sprite


class Map:
    def __init__(self, height, width, obj):
        self.height = height
        self.width = width
        self.obj = obj
        self.pd = c.newpad(height, width)


class MapObject:
    def __init__(self, start_y, start_x, string_shown, block=True, **door):
        self.start_y, self.start_x = start_y, start_x
        self.string_shown = string_shown
        self.block = block
        self.door = door


class Interactive(MapObject):
    overworld_text = []
    actions = {}         # {after_text_id: func}

    def __init__(self, start_y, start_x, string_shown, block=True, detect=None):
        super().__init__(start_y, start_x, string_shown, block)
        self.detect = detect

    def on_interacted_with(self, player, graphics, text, choice):
        for i, txt in enumerate(self.overworld_text):
            print_text(text, txt, -1)
            if i in self.actions.keys():
                self.actions[i](player, graphics, text, choice)

        text.erase()
        choice.erase()


class GrassPatch(Interactive):
    """
    A patch of "grass" that spawns wild CGs.
    The `spawn` list holds the spawning info:
    - Each item is a tuple with 2 elements.
    - The first element is the spawn rate of a given CG
      *plus the element before itself*; this is for more elegant code.
    - The second element is the name of this CG.
    """
    def __init__(self, start_y, start_x, height, width, spawn: list, levels: list):
        super().__init__(start_y, start_x, ('/' * width + '\n') * height, False)
        self.spawn = spawn
        self.levels = levels

    def on_interacted_with(self, player, graphics, text, choice):
        rand = random()
        for chance, species in self.spawn:
            if rand < chance:
                import creagrams as cg  # noqa (used in eval(), PC doesn't know that)
                CGBattle(player, eval("cg.%s(text, %d)"
                                      % (species, rand_choice(self.levels))),
                         graphics, text, choice).start_battle()
                break


class Trainer(MapObject):
    def __init__(self, pos, name, team: list, sprite, repr_char=None):
        super().__init__(pos[0], pos[1], repr_char if repr_char else name[0])
        self.name = name
        self.team = team
        self.sprite = sprite


class Player(Trainer):
    def __init__(self, name, team):
        super().__init__((10, 10), name, team, player_battle_sprite)


class Opponent(Trainer, Interactive):
    def __init__(self, pos, name, start_text, lose_text, team: list, sprite, repr_char=None, detect=None):
        super().__init__(pos, name, team, sprite, repr_char)
        self.detect = detect
        self.start_text = start_text
        self.lose_text = lose_text
        self.overworld_text = [start_text]
        self.actions = {0: self.start_battle_with_self}

        self.battled = False

    def start_battle_with_self(self, player, graphics, text, choice):
        if not self.battled:
            CGBattle(player, self, graphics, text, choice, False).start_battle()
            self.battled = True
            self.overworld_text = [self.lose_text]
            self.detect = None


class PlayerOnMap(MapObject):
    def __init__(self):
        super().__init__(10, 10, 'p')
