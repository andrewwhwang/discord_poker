class Pot():
    def __init__(self, name, players, max_per):
        self.players_chips = {p:0 for p in players} # list of tuple (player, chips)
        # self.total = total
        self.name = "Main Pot" if name == "0" else "Side Pot "+name
        self.max_per = max_per

    def __str__(self):
        eligible = ", ".join([pc.name for pc in self.players_chips.keys()])
        return '%s: $%s\t(%s are eligible to take)' % (self.name, self.get_total(),eligible)

    def get_total(self):
        return sum(list(self.players_chips.values()))

    def add_chips_to_player(self, player, chips):
        if self.players_chips[player] + chips > self.max_per:
            self.players_chips[player] = self.max_per
        else:
            self.players_chips[player] += chips


class Pots():
    def __init__(self, players):
        self.list_pots = []
        unique_list = sorted(list(set([p.chips for p in players])))
        current_max = 0
        for i, x in enumerate(unique_list):
            player_list = [p for p in players if p.chips > current_max]
            self.list_pots.append(Pot(str(i),player_list,x-current_max))
            current_max = x
    def add_bet(self, player, bet):
        for pot in self.list_pots:
            if bet > 0 and player in pot.players_chips.keys():
                max_left = pot.max_per - pot.players_chips[player]
                amount = min(max_left, bet)
                pot.add_chips_to_player(player,amount)
                bet -= amount

    def __str__(self):
        return "\n".join([str(pot) for pot in self.list_pots if pot.get_total() > 0])

# import player
# a = player.Player('a',startingChips=2130)
# b = player.Player('b',startingChips=110)
# c = player.Player('c',startingChips=600)
# d = player.Player('d',startingChips=960)
# pots = Pots([a, b, c, d])
# pots.add_bet(a, 430)
# pots.add_bet(b, 20)
# pots.add_bet(c, 430)
# pots.add_bet(d, 20)
# print(pots)
