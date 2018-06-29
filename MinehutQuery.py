import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from discord.ext.commands import Bot
from discord.ext import commands
import os
from mcstatus import MinecraftServer

bot = commands.Bot(command_prefix="!")

language = {
    "footer":"Powered By MinehutQuery | Created By Sargera",
    "ping_command_desc": "This command allows you to ping the status of any minehut server, using either its direct IP address or simply the name of the server.",
    "ts_command_desc":"Use the reactions to cycle through the differant server ids found within the below embed. This will let you see more descriptive summaries.",
    "ts_command_tooltip":"Select from the list of current top servers"
    }

@bot.event
async def on_ready():
    print("[CONSOLE] Running 'MinehutQuery' Version 1.1 (Author: Sargera)")
    await bot.change_presence(game=discord.Game(name="Minehut's Data", type=3))

@bot.command(pass_context = True)
async def ping(ctx, server_query=None):
    if ".minehut.gg" in server_query:
        server_ping = MinecraftServer.lookup(server_query)
        server_name = server_query.split(".", 1)
        server_address = server_query
    else:
        server_name = server_query
        server_address = server_query + ".minehut.gg"
        server_ping = MinecraftServer.lookup(str(server_address))
        
    get_status = server_ping.status()
    embed = discord.Embed(title=":white_check_mark: Command Response: Ping", description=language['ping_command_desc'], color=0x206694)
    embed.add_field(name="Server Name", value="```{}```".format(server_query))
    embed.add_field(name="Direct Server Connect", value="```{}```".format(server_address))
    embed.add_field(name="Players", value="```{}/{}```".format(get_status.players.online, get_status.players.max), inline=False)
    embed.add_field(name="Server Motd", value="```{}{}```".format(get_status.description['extra'][0]['text'], get_status.description['extra'][1]['text']), inline=False)
    embed.set_footer(text=language['footer'],icon_url="https://i.imgur.com/uc1QL9o.png")
    await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(pass_context = True)
async def topservers(ctx, number=None):
    response = requests.get('https://pocket.minehut.com/network/top_servers')
    top_servers = response.json()
    loop_number = 0

    server_list = []
    
    if number == None:
        loop_number = 1
        for server in top_servers['servers']:
            server_name = server['name']
            server_name = server_name
            server_list.append("[{}]: {}".format(loop_number, server_name))
            loop_number = loop_number + 1

        server_list = ("\n".join(server_list))
            
        embed = discord.Embed(title=":white_check_mark: Command Response: TopServers", description=language['ts_command_desc'], color=0x206694)
        embed.set_footer(text=language['footer'],icon_url="https://i.imgur.com/uc1QL9o.png")
        embed.add_field(name=language['ts_command_tooltip'], value="```{}```".format(server_list))
        embed_message = await bot.send_message(ctx.message.channel, embed=embed)
        await bot.add_reaction(embed_message, emoji="\U0001f4c4")
        await bot.add_reaction(embed_message, emoji="\U0000274c")
        await bot.add_reaction(embed_message, emoji="1\u20e3")
        await bot.add_reaction(embed_message, emoji="2\u20e3")
        await bot.add_reaction(embed_message, emoji="3\u20e3")
        await bot.add_reaction(embed_message, emoji="4\u20e3")
        await bot.add_reaction(embed_message, emoji="5\u20e3")

        while True:
            close = await bot.wait_for_reaction(['\U0001f4c4', '\U0000274c', '1\u20e3', '2\u20e3', '3\u20e3', '4\u20e3','5\u20e3'], message=embed_message, user=ctx.message.author)
            
            if close[0].emoji == "\U0000274c":
                await bot.delete_message(embed_message)
                await bot.delete_message(ctx.message)
                break

            if close[0].emoji == "\U0001f4c4":
                response = requests.get('https://pocket.minehut.com/network/top_servers')
                top_servers = response.json()
                await bot.edit_message(embed_message, embed=embed)

            else:
                index = int(close[0].emoji[0]) - 1
                server_name = top_servers['servers'][index]['name']
                player_count = top_servers['servers'][index]['playerCount']
                max_count = top_servers['servers'][index]['maxPlayers']
                status = top_servers['servers'][index]['status']
                motd = top_servers['servers'][index]['motd']
                online_players = top_servers['servers'][index]['players']
                online_players = "\n".join(map(str, online_players)).replace("None", "(Error obtaining player)")

                server_one_embed = discord.Embed(title=":white_check_mark: Command Response: TopServers", description=language['ts_command_desc'], color=0x206694)
                server_one_embed.set_footer(text=language['footer'])
                server_one_embed.add_field(name="Server Name", value="```[{}]: {}```".format(index, server_name))
                server_one_embed.add_field(name="Direct Connect", value="```{}.minehut.gg```".format(server_name))
                server_one_embed.add_field(name="Server MOTD", value="```{}```".format(motd), inline=False)
                server_one_embed.add_field(name="Server Slots", value="```{}/{}```".format(player_count, max_count), inline=False)
                server_one_embed.add_field(name="Server Status", value="```{}```".format(status), inline=False)
                server_one_embed.add_field(name="Online Players", value="```{}```".format(online_players), inline=False)
                await bot.edit_message(embed_message, embed=server_one_embed)

            await bot.remove_reaction(embed_message, close[0].emoji, ctx.message.author)

@bot.command(pass_context = True)
async def stats(ctx):
    response = requests.get('https://pocket.minehut.com/network/simple_stats')
    network_stats = response.json()

    player_count = network_stats['player_count']
    server_count = network_stats['server_count']
    max_servers = network_stats['server_max']
    ram_usage = network_stats['ram_count']
    ram_usage_str = str(ram_usage)[:3]

    embed = discord.Embed(title=":white_check_mark: Command Response: Stats", description="Shows some stats about minehut also found on the homepage of Minehut.com")
    embed.set_footer(text=language['footer'], icon_url="https://i.imgur.com/uc1QL9o.png")
    embed.add_field(name=":mega:  Players Online", value="```{} players online```".format(player_count), inline=False)
    embed.add_field(name=":computer:  Servers Active", value="```Current: {} active servers\nMaximum: {} servers```".format(server_count, max_servers), inline=False)
    embed.add_field(name=":rocket:  Ram Usage", value="```Current Usage: {}GB\nMaximum: {}GB```".format(ram_usage_str, "512"), inline=False)
    embed_message = await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(pass_context = True)

async def status(ctx):
    load_page = requests.get("https://twitter.com/MinehutMC")
    parse_page = BeautifulSoup(load_page.content, "html.parser")
    get_latest_status = parse_page.select_one(".js-tweet-text-container .TweetTextSize--normal").get_text()
    embed = discord.Embed(title=":white_check_mark: Command Response: Status", description="Shows the status of the Minehut status and some potentially useful other information regarding status.")

    try:
        server_ping = MinecraftServer.lookup("minehut.com")
        status = server_ping.status()
        server_latency = status.latency
        server_motd = status.description

        server_motd_append = []
        for element in range(0, 7):
            server_motd_append.append(server_motd['extra'][element]['text'])
        server_motd_formatted = "".join(map(str, server_motd_append))
        
        embed.add_field(name=":zap: Status", value="```Received a response in {}ms!\nMinehut is online.```".format(server_latency), inline=False)
    except:
        embed.add_field(name=":zap: Status", value="```Unable to retrieve ping response!\nMinehut is potentially offline.```", inline=False)

    embed.set_footer(text=language['footer'], icon_url="https://i.imgur.com/uc1QL9o.png")
    embed.add_field(name=":newspaper2: MOTD", value="```{}```".format(server_motd_formatted), inline=False)
    embed.add_field(name=":pushpin: Latest Tweet", value="```{}```".format(get_latest_status), inline=False)
    await bot.send_message(ctx.message.channel, embed=embed)
    
bot.run(os.getenv("discord_api_key"))
