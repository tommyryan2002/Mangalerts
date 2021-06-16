import os
import discord
from discord.client import Client
from dotenv import load_dotenv
import ruka_requests
import rukaDB

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print( f'''{bot.user} has connected to the {guild.name} server!
Members: ''')
    async for member in guild.fetch_members():
        print("- " + member.name)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

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
        desc = ruka_requests.grab_manga_description(title)
        await message.channel.send(desc)  

    if message.content == "r!add_guild":
        try:
            rukaDB.add_guild(str(message.guild))
            response = f"{message.guild} added to the Database!"
        except:
            response = f"Failed to add {message.guild} to the Database"
        await message.channel.send(response)

    if message.content == "r!add_user":
        try:
            rukaDB.add_user(str(message.guild), str(message.author))
            response = f"{message.author} added to the Database!"
        except:
            response = f"Failed to add {message.author} to the Database"
        await message.channel.send(response)
        
    elif message.content == "ping":
        response = "pong"
        await message.channel.send(response) 

bot.run(TOKEN)