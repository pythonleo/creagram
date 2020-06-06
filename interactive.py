from funcs import print_text


class Interactive:
    overworld_text = []
    actions = {}         # {after_text_id: func}

    def on_interacted_with(self, player, graphics, text, choice):
        for i, txt in enumerate(self.overworld_text):
            print_text(text, txt, -1)
            if i in self.actions.keys():
                self.actions[i](player, graphics, text, choice)


class Trainer:
    def __init__(self, name, team: list, sprite, repr_char=None):
        self.name = name
        self.team = team
        self.sprite = sprite
        self.repr_char = repr_char if repr_char else name[0]


class Opponent(Trainer, Interactive):
    def __init__(self, name, start_text, lose_text, team: list, sprite, repr_char=None):
        super().__init__(name, team, sprite, repr_char)
        self.start_text = start_text
        self.lose_text = lose_text
        self.overworld_text = [start_text]
        self.actions = {0: self.start_battle_with_self}

    def start_battle_with_self(self, player, graphics, text, choice):
        from cg_battle import CGBattle
        CGBattle(player, self, graphics, text, choice, False).start_battle()
