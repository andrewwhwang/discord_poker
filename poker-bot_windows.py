import discord
import random
import asyncio
from texasholdem import Texasholdem
from PIL import Image
from praw import Reddit
from itertools import islice
from os import remove

game_ongoing = False
client = discord.Client()
game = None
player_list = None
num_com_cards = 0

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global game_ongoing
    global game
    global player_list
    global num_com_cards

    if message.content == "!help":
        await client.send_message(message.channel,"```Poker-bot by Andrew --version 0.5\n\n"
        "Recognized commands:\n"
        "\t!help\t     Displays this message\n"
        "\t!startgame\tStarts an game of texas holdem\n"
        "\t!stopgame\t Ends the current game for everyone\n"
        "\t!quit\t     Removes only you from the current game(not sure if working)\n"
        "\t!join\t     Join the current game(doesn't work)\n"
        "\t!status\t   Repeats the status of the game\n"
        "\t!(C)all\t   Call\n"
        "\t!(C)heck\t  Check\n"
        "\t!(F)old\t   Fold\n"
        "\t!(R)aise x\tRaise by x amount\n```")

    elif message.content.lower().startswith('!just'):
        r = Reddit(user_agent='asdfasdfasdf')
        subreddit = r.get_subreddit("justfuckmyshitup")
        a = subreddit.get_top_from_all(limit=200)
        rand = random.randint(0,200)
        await client.send_message(message.channel, nth(a,rand).url)

    elif message.content.lower().startswith('!me_irl'):
        r = Reddit(user_agent='asdfasdfasdf')
        subreddit = r.get_subreddit("me_irl")
        a = subreddit.get_top_from_all(limit=200)
        rand = random.randint(0,200)
        await client.send_message(message.channel, nth(a,rand).url)

    elif message.content =='!startgame' and not game_ongoing:
        game_ongoing = True
        player_list = []
        time = 20 ###########debug = 5 normal = 20
        tmp = await client.send_message(message.channel, "```Who's playing?\n"
                                                        "Enter game by saying: me\n"
                                                        "Time left:"+str(time)+"```")
        start_time = tmp.timestamp
        tmp_time = time
        while tmp_time > 0:
            await asyncio.sleep(1)
            tmp_time -= 1
            await client.edit_message(tmp, "```Who's playing?\n"
                                            "Enter game by saying: !me\n"
                                            "Time left:"+str(tmp_time)+"```")
        async for log in client.logs_from(message.channel, limit=20):
            diff = (log.timestamp - start_time).total_seconds()
            if (diff < time and diff > 0 and log.content == "!me"
                and (log.author not in player_list)):
                player_list.append(log.author)
        if len(player_list) >= 1:##############################normal = 2
            await client.send_message(message.channel, "```Players registered:\n\t"+
                                                        "\n\t".join(str(e) for e in player_list)+
                                                        "\nIs this correct? !yes/!no```")
            confirmation = await client.wait_for_message(check=check)
            if confirmation.content == "!no":
                game_ongoing = False
                await client.send_message(message.channel, "```Exiting game```")
            elif confirmation.content == "!yes":
                game = Texasholdem([str(e) for e in player_list])
        else:
            await client.send_message(message.channel, "```Not enough people joined```")
            game_ongoing = False
    elif (game_ongoing and game != None and message.content.startswith('!') and
            str(message.author) in [x.name for x in game.players]):
        if message.content == "!stopgame":
            await client.send_message(message.channel,"```You sure? !yes/!no```")
            confirmation2 = await client.wait_for_message(check=check)
            if confirmation2.content == "!yes":
                game_ongoing = False
                await client.send_message(message.channel, "```Exiting game```")
        elif message.content == "!quit":
            player_list.remove(message.author)
            for p in game.players:
                if p.name == str(message.author):
                    game.losers.append(p)
        elif message.content == "!status":
            await client.send_message(message.channel, create_message(game))
            if len(game.com_cards) != 0 and len(game.com_cards) != num_com_cards:
                await client.send_file(message.channel,combine_png(game.com_cards, "community"), content="Community Cards:")
######################################################################
        else:
            command = game.parse(message.content, str(message.author))
            if command != None:
                game_rounds = game.round
                update_player_list(game.losers)
                if command == 0:
                    for i, p in enumerate(player_list):
                        await client.send_file(p, combine_png([str(c) for c in game.players[i].hand.cards], str(p)))
                        remove('tmp/'+str(p)+'.png')
                await client.send_message(message.channel, create_message(game))
                # if game.com_cards != []:
                if len(game.com_cards) != 0 and len(game.com_cards) != num_com_cards:
                    await client.send_file(message.channel,combine_png(game.com_cards, "community"), content="Community Cards:")
                num_com_cards = len(game.com_cards)


def check(msg):
    return msg.content == '!yes' or msg.content == '!no'

def update_player_list(quitters):
    global player_list
    player_list = [p for p in player_list if str(p) not in [str(s) for s in quitters]]


def combine_png(cards, name):
    pngs = ["resources/"+str(c)+".jpg" for c in cards]
    images = list(map(Image.open, pngs))
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    new_im.save('tmp/'+name+'.png')
    return 'tmp/'+name+'.png'

def create_message(game):
    previous = game.previous
    players = game.players
    pots = game.pots
    if "had" in previous:
        standings = "\n".join([p.name+" now has $"+str(p.chips) for p in players])
        msg = previous+"\n```\n"+standings+"\n```\n!ok to continue"
    else:
        msg = previous+"\n```\n"
        msg += "  Players        Chips    Blinds    Bets    Status\n"
        msg += "——————————————————————————————————————————————————\n"
        for p in players:
            action_char = "  "
            if p == players[game.action]:
                action_char = "→ "

            spaces = " " * (8 - len(str(p.chips)))
            blind_char = "—"
            post_space_counter = 10
            if p == players[game.b_index]:
                blind_char = "b"
                post_space_counter-=2
            elif p == players[game.B_index]:
                blind_char = "B"
                post_space_counter-=2
            if p == game.players[game.dealer % len(game.players)]:
                if blind_char == "—":
                    blind_char = "D"
                    post_space_counter-=2
                else:
                    blind_char += "D"
                    post_space_counter-=2
            post_spaces = " " * post_space_counter
            blind_char = spaces + blind_char + post_spaces

            status_char = "\n"
            if p in game.folded_players:
                status_char = "F\n"
            if p.chips <= 0:
                status_char = "A\n"
            name = p.name[:11] + " " * (11 - len(p.name[:11]))
            current = str(p.get_current_bet()) + " " * (8 - len(str(p.get_current_bet())))
            msg += action_char + name + "    $" + str(p.chips) + blind_char + current + status_char
        msg += "\n```\n"
        msg += str(pots) +"\n\n"
        msg += "@"+players[game.action].name + ", it's your turn. Respond with:\n!(R)aise\t!(C)all\t!(F)old"
    return msg

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)


import password
client.run(password.token)
