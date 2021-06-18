import os
import discord
from discord.client import Client
from dotenv import load_dotenv
import ruka_requests
import rukaDB
import ruka_rss
import time
import threading
import datetime



load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
bot = discord.Client(intents=intents)

db_thread = threading.Thread()
#rss_thread = threading.Thread()

def check_updates():
    old_data = ruka_rss.grab_rss_data()
    while True:
        print("Checked RSS")
        new_data = ruka_rss.grab_rss_data()
        if new_data != old_data:
            print("New Manga Releases!")
            old_set = set(old_data)
            new_releases = [manga for manga in new_data if manga not in old_set]
        #TODO: notify users here/ store recent releases on a db
        time.sleep(60)
        old_data = new_data

def notify_users(title: str):
    guilds = rukaDB.get_all_guilds()
    for guild in guilds:
        if rukaDB.manga_in_guild(guild, title):
            users = rukaDB.get_guild_users(guild)
            for user in users:
                if rukaDB.manga_is_tracked(guild, user, title): #and status date is not todays date:
                    #TODO: Notify User via DM
                    pass










@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

#TODO: when removed or added to a guild update the database by removing or adding a document
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

    if message.content[:8] == 'r!manga ':
        string = message.content
        title = string.replace('r!manga ', '')
        desc_raw = ruka_requests.grab_manga_description(title)
        title_real = ruka_requests.grab_manga_title(title)
        ele = desc_raw[0]
        desc= ''
        for ele in desc_raw:
            if ele == '[':
                break
            desc += ele
        id = ruka_requests.grab_manga_id(title)
        if id is not None:
            cover = ruka_requests.grab_cover_id(id)
            link = f'https://mangadex.org/title/{id}'
            embed=discord.Embed(title= title_real, url = link, description = desc, color=0xffbe33)
            embed.set_author(name='Ruka <3', icon_url='https://i.pinimg.com/564x/fb/29/48/fb29482d6d0e1e88a1b58c6c9d123cc4.jpg')
            embed.set_image(url=f'https://uploads.mangadex.org/covers/{id}/{cover}')
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"{title} not found on MangaDex!")

    if message.content == "r!add_guild":
        if not rukaDB.guild_in_db(str(message.guild)):
            try:
                rukaDB.add_guild(str(message.guild))
                response = f"{message.guild} added to the database!"
            except:
                response = f"Failed to add {message.guild} to the database"
        else:
            response = f"{message.guild} already in the database!"
        await message.channel.send(response)

    if message.content == "r!add_user":
        if not rukaDB.user_in_guild(str(message.guild), str(message.author)):
            try:
                rukaDB.add_user(str(message.guild), str(message.author))
                response = f"{message.author} added to the database!"
            except:
                response = f"Failed to add {message.author} to the database"
        else:
            response = f"{message.author} already in the database!"
        await message.channel.send(response)
        
    if message.content[:14] == "r!track_manga ":
        if not rukaDB.user_in_guild(str(message.guild), str(message.author)):
            try:
                rukaDB.add_user(str(message.guild), str(message.author))
                response1 = f"{message.author} added to the database!\n"
            except:
                response1 = f"Failed to add {message.author} to the database"
        else:
            response1 = ''
        string = message.content
        title = string.replace('r!track_manga ', '')
        real_title = ruka_requests.grab_manga_title(title)
        if not rukaDB.manga_is_tracked(str(message.guild), str(message.author), real_title):
            if real_title != "Manga Not Found":
                try:
                    rukaDB.add_manga(str(message.guild), str(message.author), real_title)
                    response = f"{message.author} is now tracking {real_title}!"
                except:
                    response = f"Error: {real_title} could not be tracked"
            else:
                response = "Manga Not Found"
        else:
            response = f"{title} is already being tracked!"
        await message.channel.send(response1 + response)

    if message.content[:16] == "r!untrack_manga ":
        string = message.content
        title = string.replace('r!untrack_manga ', '')
        real_title = ruka_requests.grab_manga_title(title)
        if real_title != "Manga Not Found":
            if rukaDB.manga_is_tracked(str(message.guild), str(message.author), real_title):
                try:
                    rukaDB.remove_manga(str(message.guild), str(message.author), real_title)
                    response = f"{message.author} is no longer tracking {real_title}!"
                except:
                    response = f"Error: {title} could not be untracked"
            else:
                response = f"{title} is already not being tracked"
        else:
            response = f"{title} not found on MangaDex"
        await message.channel.send(response)

    if message.content == "r!untrack_all_manga":
        try:
            rukaDB.remove_all_manga(str(message.guild), str(message.author))
            response = f"{message.author} is no longer tracking any manga!"
        except:
            response = f"Error: Manga could not be untracked"
        await message.channel.send(response)

    if message.content == "r!my_manga":
        string = ""
        try:
            manga_list = rukaDB.get_user_manga(str(message.guild), str(message.author))
            if len(manga_list) == 0:
                response = f'> {message.author} is not tracking any manga!'
                await message.channel.send(response)
            else:
                for manga in manga_list:
                    string += '⁠— ' + manga + '\n'
                embed = discord.Embed(title=f"{message.author}'s Tracked Manga", description=string, color=0xffbe33)
                embed.set_author(name= "Ruka <3", icon_url='https://i.pinimg.com/564x/fb/29/48/fb29482d6d0e1e88a1b58c6c9d123cc4.jpg')
                embed.set_thumbnail(url = message.author.avatar_url)
                await message.channel.send(embed=embed)
        except:
            response = f'Error: could not retrieve manga for {message.author}'
            await message.channel.send(response)

    elif message.content == "ping":
        response = "pong"
        await message.channel.send(response) 


#db_thread.start()
#rss_thread.start()
bot.run(TOKEN)