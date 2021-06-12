import os
import discord
from discord.client import Client
from dotenv import load_dotenv
import ruka_requests

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
bot = discord.Client(intents=intents)

def grab_manga(name: str) -> str:
    pass


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

    if message.author.name == "ArrisKing16":
        response = "foliage lookin ass"
        await message.channel.send(response)

    if bot.user.mentioned_in(message):
        await message.add_reaction('GWnoneAngryPing:644364665987661825') 

    if message.content[:11] == 'r!manga_id ':
        string = message.content
        title = string.replace('r!manga_id ', '')
        id = ruka_requests.grab_manga_id(title)
        await message.channel.send(id)

    if message.content[:13] == 'r!manga_desc ':
        string = message.content
        title = string.replace('r!manga_desc ', '')
        id = ruka_requests.grab_manga_description(title)
        await message.channel.send(id)  

    elif message.content == "ping":
        response = "pong"
        await message.channel.send(response) 

bot.run(TOKEN)