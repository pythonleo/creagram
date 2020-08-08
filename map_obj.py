from funcs import print_text
import curses as c


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


class Interactive:
    overworld_text = []
    actions = {}         # {after_text_id: func}

    def on_interacted_with(self, player, graphics, text, choice):
        for i, txt in enumerate(self.overworld_text):
            print_text(text, txt, -1)
            if i in self.actions.keys():
                self.actions[i](player, graphics, text, choice)


class InterTest(MapObject, Interactive):
    def __init__(self, y, x):
        super().__init__(y, x, 'i')
        self.overworld_text = ['hello world']


class Trainer(MapObject):
    def __init__(self, pos, name, team: list, sprite, repr_char=None):
        super().__init__(pos[0], pos[1], repr_char if repr_char else name[0])
        self.name = name
        self.team = team
        self.sprite = sprite


class Opponent(Trainer, Interactive):
    def __init__(self, pos, name, start_text, lose_text, team: list, sprite, repr_char=None):
        super().__init__(pos, name, team, sprite, repr_char)
        self.start_text = start_text
        self.lose_text = lose_text
        self.overworld_text = [start_text]
        self.actions = {0: self.start_battle_with_self}

    def start_battle_with_self(self, player, graphics, text, choice):
        from cg_battle import CGBattle
        CGBattle(player, self, graphics, text, choice, False).start_battle()


class PlayerOnMap(MapObject):
    def __init__(self):
        super().__init__(10, 10, 'p')
