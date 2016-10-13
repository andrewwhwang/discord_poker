import deck
import hand
import card
import pot
import player
import random

class Texasholdem():
    def __init__(self, players, smallBlind=10, bigBlind=20, dealer=0):
        self.players = [player.Player(p) for p in players]
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        self.deck = deck.Deck()
        self.com_cards = []
        self.hole_cards = []
        self.round = 0
        self.pots = pot.Pots(self.players)
        self.previous = ""
        self.losers = []
        self.dealt = False
        self.action = 0
        self.dealer = dealer

    def get_b(self):
        return (1 + self.dealer) % len(self.players)

    def get_B(self):
        return (2 + self.dealer) % len(self.players)

    def deal_player(self, player):
        player.hand = hand.Hand(self.deck.draw(2))
        print(player.name, player.hand)
        return [str(c) for c in player.hand.cards]

    def setup_game(self):
        print("setting up game")
        #to work, needs self.dealer to be correct
        self.hole_cards = []
        self.pots = pot.Pots(self.players)
        self.com_cards = []
        self.deck = deck.Deck()
        self.round = 0
        self.reset_action()
        self.previous = ""
        for i, player in enumerate(self.players):
            player.has_folded = False
            player.hand = []
            self.hole_cards.append(self.deal_player(player))
            # print(self.hole_cards)
            #setups up blinds
            if i == self.get_b():
                player.SB = True
                player.BB = False
                bet = min(self.smallBlind,player.chips)
                self.pots.add_bet(player, bet)
                player.current_bet = bet
                player.change_chips(-1*bet)
            elif i == self.get_B():
                player.SB = False
                player.BB = True
                bet = min(self.bigBlind,player.chips)
                self.pots.add_bet(player, bet)
                player.current_bet = bet
                player.change_chips(-1*bet)

                self.highest_bet = self.bigBlind
            else:
                player.SB = False
                player.BB = False

            #resets the dealer position
            if i == self.dealer:
                player.dealer = True
            else:
                player.dealer = False

            #resets the action position
            if i == self.action:
                player.action = True
            else:
                player.action = False
            player.has_acted = False

        if self.players[self.action].chips <= 0:
            self.increment_action()

    def increment_action(self):
        #find next player that hasn't folded and still has money

        self.action = (self.action + 1) % len(self.players)
        while self.players[self.action].has_folded or self.players[self.action].chips <= 0:
            self.action = (self.action + 1) % len(self.players)
        #setup the player obj's action boolean
        for i, player in enumerate(self.players):
            if i == self.action:
                player.action = True
            else:
                player.action = False

        #get players that haven't folded
        remaining = [p for p in self.players if not p.has_folded]
        #get players that still have money
        remaining2 = [p for p in self.players if not p.chips > 0]

        #winner if everyone else folded
        if len(remaining) == 1:
            self.winner()

        #everyone reached agreed bet amount
        elif self.players[self.action].has_acted:
            self.next_round()

        elif len(remaining2) == 1:
            while self.round <= 3:
                self.next_round()



    def reset_action(self):
        if self.round == 0:
            self.action = (3 + self.dealer) % len(self.players)
        else:
            self.action = (1 + self.dealer) % len(self.players)


    def next_round(self):
        self.losers = []
        # print([p.hand for p in self.players])
        # for p in self.players:
        #     print(p.name, p.chips, p.has_folded)
        self.round += 1
        self.reset_action()
        if self.round <= 3:
            if self.round != 0:
                self.hole_cards = []
            def map_rounds(num):
                if num == 1:
                    return 3
                if num == 2:
                    return 1
                if num == 3:
                    return 1
                return 0
            num_cards = map_rounds(self.round)
            draw = self.deck.draw(num_cards)
            for p in self.players:
                p.hand += draw
                # print(p, p.hand)
                p.has_acted = False
            self.com_cards += list(draw)
            print(self.com_cards)
        else:
            self.winner()

        # if len([p for p in self.players if p.chips > 0 or not p.has_folded]):
        #     next_round()

    def winner(self):
        winners = []
        for pot in self.pots.list_pots:
            if len(pot.players_chips) > 1:
                players = [p for p in self.players if p in pot.players_chips.keys() and not p.has_folded]
                players.sort(key=lambda p: p.hand, reverse=True)
                winners = [players[0]]
                for p in players[1:]:
                    if p.hand == players[0].hand:
                        winners.append(p)
                bounty = pot.get_total() // len(winners)
                for p in players:
                    if p in winners:
                        p.change_chips(bounty)
            else:
                list(pot.players_chips.keys())[0].change_chips(list(pot.players_chips.values())[0])
        hands = [p.name+" had a "+hand.Hand(p.hand.cards).str_sym()[5:-1] for p in self.players if not p.has_folded]
        multi_line = "\n".join(hands)
        self.previous = multi_line

        for p in self.players:
            if p.chips <= 0:
                self.losers.append(p)
        self.players = [p for p in self.players if p.chips > 0]
        #get non folded players and reveal their cards
        self.dealer += 1
        self.dealt = False
        print("==========================endofgame==========================")
        # self.setup_game()

    def call(self, player):
        bet = min(self.highest_bet - player.current_bet, player.chips)
        # print(player.name,bet)
        self.pots.add_bet(player, bet)
        player.chips -= bet
        player.current_bet += bet
        player.has_acted = True

    def fold(self, player):
        player.has_folded = True
        player.has_acted = True

    def raise_up(self,player,num):
        self.highest_bet += num
        bet = min(self.highest_bet - player.current_bet, player.chips)
        print(player.name,bet)
        self.pots.add_bet(player, bet)
        player.chips -= bet
        player.current_bet += bet


        for p in self.players:
            if not p.has_folded:
                p.has_acted = False
        player.has_acted = True
        #set everyone thats still in to has_acted = False

    def parse(self, command, player_str):
        if not self.dealt:
            self.setup_game()
            self.dealt = True
        else:
            self.hole_cards = []
            player = self.players[self.action]
            if player_str == player.name:
                if command.lower() == "!c" or command.lower() == "!call" or command.lower() == "!check":
                    self.call(player)
                    self.previous = player_str+" has called/checked"
                elif command[:3].lower() == "!r " or command[:7].lower() == "!raise ":
                    bet = 0
                    try:
                        if command[:3].lower() == "!r ":
                            bet = int(command[3:])
                        elif command[:7].lower() == "!raise ":
                            bet = int(command[7:])
                    except:
                        return None
                    if bet > player.chips or bet <= 0:
                        return None
                    self.raise_up(player,bet)
                    self.previous = player_str+" has raised by " + str(bet)
                elif command.lower() == "!f" or command.lower() == "!fold":
                    player.has_folded = True
                    self.previous = player_str+" has folded"
                else:
                    return None
                self.increment_action()
            else:
                return None
        return 1


def create_message(players, previous, pots):
    action_str = ""
    if "had" in previous:
        standings = "\n".join([p.name+" now has $"+str(p.chips) for p in players])
        msg = "```\n"+previous+"\n"+standings+"\ntype !ok to continue\n```"
    else:
        msg = previous+"\n```\n"
        msg += "\tPlayers\t    Chips\tBlinds\tBets\tStatus\n"
        for p in players:
            action_char = "\t"
            if p.action:
                action_char = "→   "
                action_str = str(p)

            blind_char = "\t\t"
            if p.SB:
                blind_char = "\t  ⓑ\t    "
            elif p.BB:
                blind_char = "\t  Ⓑ\t    "

            status_char = "\n"
            if p.has_folded:
                status_char = "\tⒻ\n"
            if p.chips <= 0:
                status_char = "\tⒶ\n"
            msg += action_char + p.name[:11] + "\t$" + str(p.chips) + blind_char + p.get_current_bet()+status_char
        msg += "\n```\n"
        msg += str(pots) +"\n"
        msg += action_str + ", it's your turn. Respond with\n!(R)aise\t!(C)all\t!(F)old"
    return msg
#
# game = Texasholdem(['ann','bob'])
# game.players[0].change_chips(-75)
# game.players[1].change_chips(-50)

# game.parse("!yes", "random")
# print(game.com_cards)
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'bob')
# print(game.com_cards)
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'ann')
# print(game.com_cards)
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'bob')
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'ann')
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'bob')
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'ann')
# print(create_message(game.players,"", game.pots))
#
#
# game.parse('!c', 'bob')
# print(create_message(game.players,"", game.pots))
#
# game.parse('!c', 'ann')
# print(create_message(game.players,game.previous, game.pots))
# game.parse("!ok", "random")
# print(create_message(game.players,game.previous, game.pots))
