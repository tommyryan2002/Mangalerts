import os
import discord
from discord.client import Client
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print( f'''{bot.user} has connected to the {guild.name} server! \n
Members: ''')
    async for member in guild.fetch_members():
        print("- " + member.name)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.author.name == "eliisprettycool":
        response = "ueno trash"
        await message.channel.send(response)

    if message.author.name == "ArrisKing16":
        response = "foliage lookin ass"
        await message.channel.send(response)

    if bot.user.mentioned_in(message):
        await message.add_reaction('GWnoneAngryPing:644364665987661825')   

    elif message.content == "ping":
        response = "pong"
        await message.channel.send(response)

    elif "games" in message.content:
        response = "I'd love to bb ;)"
        await message.channel.send(response)        
        

bot.run(TOKEN)