import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from mcstatus import MinecraftServer
import os
from tinydb import TinyDB, Query

database = TinyDB('mhq_database.json')
server = Query()

async def get_prefix(bot, message):  
    if not database.search(server.server_id == message.server.id):
        database.insert({"server_id":str(message.server.id), "prefix": "?mh "})

    preferences = database.search(server.server_id == message.server.id)
    prefix = preferences[0]['prefix']
    return prefix

bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command("help")

language = {
    "footer":"Powered By MinehutQuery | Created By Sargera",
    "ping_command_desc": "This command allows you to ping the status of any minehut server, using either its direct IP address or simply the name of the server.",
    "ts_command_desc":"Use the reactions to cycle through the differant server ids found within the below embed. This will let you see more descriptive summaries.",
    "ts_command_tooltip":"Select from the list of current top servers",
    "theme":0x2ECC71,
    "changeprefix_command_desc": "Allows administrators to change the prefix used to activate MinehutQuery commands.Something to note is that Discord does not register spaces by default. You will need to add a ** at the end of your command to add a space."
    }

@bot.command(pass_context = True)
async def changeprefix(ctx, new_prefix):
    try:
        new_prefix = new_prefix.replace("**", " ") 
        database.update({"prefix":str(new_prefix)}, server.server_id == ctx.message.server.id)
        embed = discord.Embed(title=":white_check_mark: Command Response: ChangeStatus", description=language['changeprefix_command_desc'], color=language['theme'])
        embed.set_footer(text=language['footer'],icon_url="https://i.imgur.com/uc1QL9o.png")
        embed.add_field(name=":rocket: Success", value="```Updated default prefix for this server!\nNew Prefix: '{}'```".format(new_prefix))
        await bot.send_message(ctx.message.channel, embed=embed)
    except:
        embed = discord.Embed(title=":white_check_mark: Command Response: ChangeStatus", description=language['changeprefix_command_desc'], color=language['theme'])
        embed.add_field(name=":x: Failed", value="```Unable to set new prefix! Please check your parameters for this command and try again.\nIf this problem persists, message Sargera.```")
        embed.set_footer(text=language['footer'],icon_url="https://i.imgur.com/uc1QL9o.png")
        await bot.send_message(ctx.message.channel, embed=embed)
        

@bot.event
async def on_server_join(server):
    print("[CONSOLE] New instance of MinehutQuery Bot runinng on {}".format(server.name))
    
@bot.event
async def on_ready():
    print("[CONSOLE] Running 'MinehutQuery' Version 1.0 (Author: Sargera)")
    await bot.change_presence(game=discord.Game(name="Minehut's Data", type=3))

@bot.command(pass_context = True)
async def ping(ctx, server_query=None):
    try:
        server_name = server_query
        server_address = server_query + ".minehut.gg"
        server_ping = MinecraftServer.lookup(str(server_address))
        get_status = server_ping.status()
        embed = discord.Embed(title=":white_check_mark: Command Response: Ping", description=language['ping_command_desc'], color=language['theme'])
        embed.add_field(name="Server Name", value="```{}```".format(server_query))
        embed.add_field(name="Direct Server Connect", value="```{}```".format(server_address))
        embed.add_field(name="Players", value="```{}/{}```".format(get_status.players.online, get_status.players.max), inline=False)
        embed.add_field(name="Server Motd", value="```{}{}```".format(get_status.description['extra'][0]['text'], get_status.description['extra'][1]['text']), inline=False)
        embed.set_footer(text=language['footer'],icon_url="https://i.imgur.com/uc1QL9o.png")
        
    except:
        embed = discord.Embed(title=":white_check_mark: Command Response: Ping", description=language['ping_command_desc'], color=language['theme'])
        embed.add_field(name=":x: Invalid usage of this command!", value="```To use this command, you must type\n [prefix]ping [name of the server you wish to ping]\nFor more details, visit [prefix]help```".format(server_query))
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
            
        embed = discord.Embed(title=":white_check_mark: Command Response: TopServers", description=language['ts_command_desc'], color=language['theme'])
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

                server_one_embed = discord.Embed(title=":white_check_mark: Command Response: TopServers", description=language['ts_command_desc'], color=language['theme'])
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

    embed = discord.Embed(title=":white_check_mark: Command Response: Stats", description="Shows some stats about minehut also found on the homepage of Minehut.com", color=language['theme'])
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
    embed = discord.Embed(title=":white_check_mark: Command Response: Status", description="Shows the status of the Minehut status and some potentially useful other information regarding status.", color=language['theme'])

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


@bot.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(title=":white_check_mark: Command Response: Help", description="Note: These commands will use whatever prefix you have set with the changePrefix command!\n\nShows help for the commands that this bot has. If you have a good idea for a command that isnt yet available, Message Sargera!", color=language['theme'])
    embed.set_footer(text=language['footer'], icon_url="https://i.imgur.com/uc1QL9o.png")
    embed.add_field(name="Status Command", value="```Shows you some information about the current status of minehut, including MOTD, tweets and online status```", inline=False)
    embed.add_field(name="Stats Command", value="```Shows you some data available on the minehut website such as ram usage, player count and more!```", inline=False)
    embed.add_field(name="Ping Command", value="```Example Usage: !ping Haste\nWill show you some basic details about that server such as player count, status and MOTD```", inline=False)
    embed.add_field(name="TopServers Command", value="```Shows you detailed information about the top servers on Minehut along with options to show you server-specific information```", inline=False)
    embed.add_field(name="Changeprefix Command", value="```Allows you to set a custom prefix that the bot will recognise when typing MinehutQuery commands.```", inline=False)
    await bot.send_message(ctx.message.channel, embed=embed)

bot.run("NDYxOTYyMzAyODk2MjA5OTIx.Dha7cw.4iFWwZOxU3qId5t4g57RJuZVjVI")
#bot.run(os.getenv("discord_api_key"))
