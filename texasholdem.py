import deck
import hand
import card
import pot
import player
import random

class Texasholdem():
    def __init__(self, players, smallBlind=10, bigBlind=20, dealer=0):
        self.players = [player.Player(p) for p in players]
        self.folded_players = []
        self.all_in_players = []
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        # self.deck = deck.Deck()
        # self.com_cards = []
        # self.hole_cards = []
        # self.round = 0
        # self.pots = pot.Pots(self.players)
        self.previous = ""
        self.losers = []
        self.dealt = False
        self.action = 0
        self.dealer = dealer

#############mini setup functions##############
    def setup_blinds(self):

        self.b_index = (1 + self.dealer) % len(self.players)
        small_blind_player = self.players[self.b_index]
        bet = min(self.smallBlind,small_blind_player.chips)
        self.pots.add_bet(small_blind_player, bet)
        small_blind_player.current_bet = bet
        small_blind_player.change_chips(-1*bet)

        self.B_index = (2 + self.dealer) % len(self.players)
        big_blind_player = self.players[self.B_index]
        bet = min(self.bigBlind,big_blind_player.chips)
        self.pots.add_bet(big_blind_player, bet)
        big_blind_player.current_bet = bet
        big_blind_player.change_chips(-1*bet)

    def setup_hole_cards(self):
        for i, player in enumerate(self.players):
            #deal player hold cards
            player.hand = hand.Hand(self.deck.draw(2))
            #
            player.has_acted = False

    def reset_action(self):
        if self.round == 0:
            self.action = (3 + self.dealer) % len(self.players)
        else:
            self.action = (1 + self.dealer) % len(self.players)
    #############main functions##############
    def setup_game(self):
        print("setting up game")
        #to work, needs self.dealer to be correct
        # self.hole_cards = []
        self.pots = pot.Pots(self.players)
        self.com_cards = []
        self.deck = deck.Deck()
        self.round = 0
        self.previous = ""
        self.folded_players = []
        self.all_in_players = []
        self.setup_hole_cards()
        self.losers = []
        
        #setups up blinds
        self.setup_blinds()
        self.highest_bet = self.bigBlind

        self.reset_action()
        self.increment_action(0)

    def increment_action(self,increment):
        #find next player that hasn't folded and still has money
        self.action = (self.action + increment) % len(self.players)
        while self.players[self.action] in self.folded_players or self.players[self.action] in self.all_in_players:
            self.action = (self.action + 1) % len(self.players)

    def check_end(self):
        #check if everyone but one person folded out
        if len(self.folded_players) == len(self.players) - 1:
            self.winner("folded")

        elif len(self.folded_players) + len(self.all_in_players) == len(self.players) - 1:
            while self.round <= 3:
                self.next_round()

        #everyone reached agreed bet amount
        elif self.players[self.action].has_acted:
            self.next_round()

    def next_round(self):
        print("--------------------------next_round--------------------------")
        com_card_map = [0,3,1,1]
        # self.losers = []
        self.round += 1
        self.reset_action()
        self.increment_action(0)
        self.highest_bet = 0
        if self.round <= 3:
            #resets hold_cards so bot doesn't pm every time
            # if self.round != 0:
            #     self.hole_cards = []

            draw = self.deck.draw(com_card_map[self.round])
            for p in self.players:
                p.current_bet = 0
                p.hand += draw
                p.has_acted = False
            self.com_cards += list(draw)
            print(self.com_cards)
        else:
            self.winner("")

        # if len([p for p in self.players if p.chips > 0 or not p.has_folded]):
        #     next_round()
    #
    def winner(self,condition):
        winners = []
        for pot in self.pots.list_pots:
            if len(pot.players_chips) >= 2:
                players = [p for p in pot.players_chips.keys() if p not in self.folded_players]
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

        if condition != "folded":
            hands = [p.name+" had a "+hand.Hand(p.hand.cards).str_sym()[5:-1] for p in self.players if p not in self.folded_players]
            multi_line = "\n".join(hands)
            self.previous = multi_line
        else:
            self.previous = str(self.players[self.action])+" had: ██, ██, ██, ██, ██"


        self.losers = [p for p in self.players if p.chips <= 0]
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
        if player.chips <= 0:
            self.all_in_players.append(player)

    def fold(self, player):
        self.folded_players.append(player)
        player.has_acted = True

    def raise_up(self,player,num):
        self.highest_bet += num + player.current_bet
        print("highest_bet = "+str(self.highest_bet))
        bet = min(self.highest_bet, player.chips)
        self.pots.add_bet(player, bet)
        player.chips -= bet
        player.current_bet += bet
        if player.chips <= 0:
            self.all_in_players.append(player)

        for p in self.players:
            if p not in self.folded_players:
                p.has_acted = False

        player.has_acted = True
        #set everyone thats still in to has_acted = False

    def parse(self, command, player_str):
        if not self.dealt:
            self.setup_game()
            self.dealt = True
        else:
            player = self.players[self.action]
            if player_str == player.name:
                if command.lower() == "!c" or command.lower() == "!call" or command.lower() == "!check":
                    self.call(player)
                    self.previous = "`"+player_str+"` has called/checked"
                elif command[:3].lower() == "!r " or command[:7].lower() == "!raise ":
                    bet = 0
                    try:
                        if command[:3].lower() == "!r ":
                            bet = int(command[3:])
                        elif command[:7].lower() == "!raise ":
                            bet = int(command[7:])
                    except:
                        return None
                    if bet + self.highest_bet > player.chips or bet < self.bigBlind:
                        return None
                    self.raise_up(player,bet)
                    self.previous = "`"+player_str+"` has raised by " + str(bet)
                elif command.lower() == "!f" or command.lower() == "!fold":
                    self.fold(player)
                    # player.has_folded = True
                    self.previous = "`"+player_str+"` has folded"
                else:
                    return None
                self.increment_action(1)
                self.check_end()
            else:
                return None
        return 1


def create_message(game):
    previous = game.previous
    players = game.players
    pots = game.pots
    if "had" in previous:
        standings = "\n".join([p.name+" now has $"+str(p.chips) for p in players])
        msg = "```\n"+previous+"\n\n"+standings+"\n```\n!ok to continue"
    else:
        msg = previous+"\n```\n"
        msg += "\tPlayers\tChips\tBlinds\tBets\tStatus\n"
        for p in players:
            action_char = "\t"
            if p == players[game.action]:
                action_char = "→\t"

            blind_char = "\t-\t"
            # spaces = " " * (5 - len(str(p.chips)))
            if p == players[game.b_index]:
                blind_char = "\tⓑ\t"
            elif p == players[game.B_index]:
                blind_char = "\tⒷ\t"

            status_char = "\n"
            if p in game.folded_players:
                status_char = "\tⒻ\n"
            if p.chips <= 0:
                status_char = "\tⒶ\n"
            msg += action_char + p.name[:11] + "\t$" + str(p.chips) + blind_char + p.get_current_bet()+status_char
        msg += "\n```\n"
        msg += str(pots) +"\n\n"
        msg += players[game.action].name + ", it's your turn. Respond with\n!(R)aise\t!(C)all\t!(F)old"
    return msg


game = Texasholdem(['ann','bob','cat'])
game.players[0].change_chips(-750)
game.players[1].change_chips(-500)

game.parse("!yes", "random")
print(create_message(game))
print("....................................................................")
game.parse('!r 100', 'ann')
print(create_message(game))
print("....................................................................")
game.parse('!r 370', 'bob')
print(create_message(game))
print("....................................................................")
game.parse('!c', 'cat')
print(create_message(game))
print("....................................................................")
game.parse('!f', 'ann')
print(create_message(game))
print("....................................................................")
# game.parse('!c', 'cat')
# print(create_message(game))
# print("....................................................................")
# game.parse('!c', 'ann')
# print(create_message(game))
# print("....................................................................")
# game.parse('!c', 'bob')
# print(create_message(game))
# print("....................................................................")
# game.parse('!c', 'cat')
# print(create_message(game))
# print("....................................................................")
# game.parse('!c', 'ann')
# print(create_message(game))
# print("....................................................................")
