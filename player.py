class Player():
    def __init__(self, name, startingChips=100):
        self.name = name
        self.chips = startingChips
        self.dealer = False
        self.SB = False
        self.BB = False
        self.hand = []
        self.current_bet = 0
        self.action = False
        self.has_acted = False
        self.has_folded = False

    def change_chips(self, num):
        self.chips += num

    def get_current_bet(self):
        if self.current_bet == 0:
            return ""
        return str(self.current_bet)

    # def __eq__(self, other):
    #     return self.name == other.name

    def __str__(self):
        return self.name
