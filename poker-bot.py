import discord
import random
import asyncio
from texasholdem import Texasholdem
from PIL import Image

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
    if message.content =='!startgame' and not game_ongoing:
        game_ongoing = True
        player_list = []
        time = 15 ###########debug = 5 normal = 20
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
        if len(player_list) >= 2:##############################normal = 2
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
                    game.players.remove(p)
        elif message.content == "!status":
            print("status")
######################################################################
        else:
            # message.content == "!c" or message.content.startswith == "!r" or message.content == "!f":
            command = game.parse(message.content, str(message.author))
            if command != None:
                game_rounds = game.round
                update_player_list(game.losers)
                if game.hole_cards != []:
                    for i, p in enumerate(player_list):
                        await client.send_file(p, combine_png(game.hole_cards[i], str(p)))
                await client.send_message(message.channel, create_message(game.players, game.previous, game.pots))
                # if game.com_cards != []:
                if len(game.com_cards) != 0 and len(game.com_cards) != num_com_cards:
                    await client.send_file(message.channel,combine_png(game.com_cards, "community"), content="Community Cards:")
                num_com_cards = len(game.com_cards)


    # for p in player_list:
    #     p_list,prev,pots,hole_msg = game.deal_player(str(p))
    #     await client.send_message(message.channel, create_message(p_list,prev,pots))
    #     await client.send_file(p, combine_png(hole_msg, str(p)))





    elif message.content == "!help":
        await client.send_message(message.channel,"```Poker-bot by Andrew --version 0.2\n\n"
        "Recognized commands:\n"
        "\t!help\t     Displays this message\n"
        "\t!startgame\tStarts an game of texas holdem\n"
        "\t!stopgame\t Ends the current game for everyone\n"
        "\t!quit\t     Removes only you from the current game(not sure if works)\n"
        "\t!status\t   Repeats the status of the game(not working)\n"
        "\t!(C)all\t   Call\n"
        "\t!(C)heck\t  Check\n"
        "\t!(F)old\t   Fold\n"
        "\t!(R)aise x\tRaise by x amount\n```")

def check(msg):
    return msg.content == '!yes' or msg.content == '!no'

def update_player_list(quitters):
    global player_list
    player_list = [p for p in player_list if str(p) not in [str(s) for s in quitters]]


def combine_png(cards, name):
    pngs = ["resources/"+str(c)+".png" for c in cards]
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

def create_message(players, previous, pots):
    action_str = ""
    if "had" in previous:
        standings = "\n".join([p.name+" now has $"+str(p.chips) for p in players])
        msg = "```\n"+previous+"\n"+standings+"\n```\n!ok to continue"
    else:
        msg = previous+"\n```\n"
        msg += "\tPlayers\t    Chips\tBlinds\tBets\tStatus\n"
        for p in players:
            action_char = "\t"
            if p.action:
                action_char = "→   "
                action_str = str(p)

            blind_char = "\t\t"
            spaces = " " * min(6 - len(str(p.chips)),0)
            if p.SB:
                blind_char = "\t"+spaces+"ⓑ\t    "
            elif p.BB:
                blind_char = "\t"+spaces+"Ⓑ\t    "

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

import password
client.run(password.token)
