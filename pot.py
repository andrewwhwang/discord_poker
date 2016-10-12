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
            return chips - self.max_per
        else:
            self.players_chips[player] += chips
            return 0


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
                bet = pot.add_chips_to_player(player,bet)

    def __str__(self):
        return "\n".join([str(pot) for pot in self.list_pots if pot.get_total() > 0])
# import player
# a = player.Player("a")
# b = player.Player("b")
# c = player.Player("c")
# a.chips =19
# b.chips =15
# c.chips = 100
# p = Pots([a,b,c])
# p.add_bet(a, 19)
# print(p)
