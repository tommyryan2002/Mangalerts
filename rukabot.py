import os
import discord
import asyncio
from discord import channel
from discord import utils
from discord.client import Client
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get 
from dotenv import load_dotenv
import ruka_requests
import rukaDB
import ruka_rss
import time
import threading
from datetime import date
import nest_asyncio

#load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
#TOKEN = os.getenv('TOKEN')
#GUILD = os.getenv('GUILD')
bot = commands.Bot(command_prefix='r!', intents = intents)

def check_updates():
    old_data = ruka_rss.grab_rss_data()
    while True:
        new_data = ruka_rss.grab_rss_data()
        print("Checked RSS")
        if new_data != old_data:
            print("New Manga Releases!")
            new_releases = [manga for manga in new_data if manga not in old_data]
            print(new_releases)
            for manga in new_releases:
                asyncio.run_coroutine_threadsafe(notify_users(ruka_requests.grab_manga_title(manga['title']), manga['chapter'], manga['group']), bot.loop)
        time.sleep(20)
        old_data = new_data

async def notify_users(title: str, chapter: str, group: str):
    if title != "Manga Not Found":
        print(f'Notifying users about: {title}')
        guilds = rukaDB.get_all_guilds()
        for guild_name in guilds:
            if rukaDB.manga_in_guild(guild_name, title):
                users = rukaDB.get_guild_users(guild_name)
                for user_name in users:
                    if rukaDB.manga_is_tracked(guild_name, user_name, title) \
                    and rukaDB.get_manga_date(guild_name, user_name, title) != date.today().strftime("%m/%d/%Y"):
                        for guild in bot.guilds:
                            if guild.name == guild_name:
                                for member in guild.members:
                                    print(member)
                                    if str(member) == user_name:
                                        rukaDB.modify_date(str(guild), str(member), title, date.today().strftime("%m/%d/%Y"))
                                        id = ruka_requests.grab_manga_id(title)
                                        cover = ruka_requests.grab_cover_id(id)
                                        search_title = title.replace(' ', '+')
                                        embed= discord.Embed(title=f"New {title} Chapter Alert!", \
                                            url=f"https://mangadex.tv/search?type=titles&title={search_title}&submit=", \
                                                description=f'A new chapter of {title} is out!', color= 0xff0000)
                                        embed.set_author(name='Mangalerts', icon_url='https://imgur.com/nMiqX4V.png')
                                        embed.add_field(name='Scan Group', value = group, inline=True)
                                        embed.add_field(name='Chapter', value=chapter, inline=True)
                                        embed.set_image(url=f'https://uploads.mangadex.org/covers/{id}/{cover}')
                                        await member.send(embed=embed)
                                        break
                            break


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

@bot.event
async def on_guild_join(guild):
    if not rukaDB.guild_in_db(str(guild)):
        try:
            rukaDB.add_guild(str(guild))
            response = f"{guild} added to the database!"
        except:
            response = f"Failed to add {guild} to the database"
    else:
        response = f"{guild} already in the database!"
    await guild.channels[0].send(response)

@bot.event
async def on_guild_remove(guild):
    if rukaDB.guild_in_db(str(guild)):
        try:
            rukaDB.remove_guild(str(guild))
            print(f"{guild} removed from the database!")
        except:
            print(f"Failed to remove {guild} from the database")
    else:
        print(f"{guild} already not in the database!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #if bot.user.mentioned_in(message):
        #await message.add_reaction('GWnoneAngryPing:644364665987661825') 

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
            embed=discord.Embed(title= title_real, url = link, description = desc, color=0xff0000)
            embed.set_author(name='Mangalerts', icon_url='https://imgur.com/nMiqX4V.png')
            embed.set_image(url=f'https://uploads.mangadex.org/covers/{id}/{cover}')
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"{title} not found on MangaDex!")

    #if message.content == "r!add_guild":
        #if not rukaDB.guild_in_db(str(message.guild)):
            #try:
                #rukaDB.add_guild(str(message.guild))
                #response = f"{message.guild} added to the database!"
            #except:
                #response = f"Failed to add {message.guild} to the database"
        #else:
            #response = f"{message.guild} already in the database!"
        #await message.channel.send(response)

    #if message.content == "r!add_user":
       # if not rukaDB.user_in_guild(str(message.guild), str(message.author)):
          #  try:
           #     rukaDB.add_user(str(message.guild), str(message.author))
          #      response = f"{message.author} added to the database!"
          #  except:
        #        response = f"Failed to add {message.author} to the database"
      #  else:
     #       response = f"{message.author} already in the database!"
     #   await message.channel.send(response)
    
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
                response = f'{message.author} is not tracking any manga!'
                await message.channel.send(response)
            else:
                for manga in manga_list:
                    string += '⁠— ' + manga + '\n'
                embed = discord.Embed(title=f"{message.author}'s Tracked Manga", description=string, color=0xff0000)
                embed.set_author(name= "Mangalerts", icon_url='https://imgur.com/nMiqX4V.png')
                embed.set_thumbnail(url = message.author.avatar_url)
                await message.channel.send(embed=embed)
        except:
            response = f'Error: could not retrieve manga for {message.author}'
            await message.channel.send(response)

    if message.content == "r!help":
        embed=discord.Embed(title="Ruka Bot Commands", color=0xff0000)
        embed.set_author(name="Mangalerts", icon_url="https://imgur.com/nMiqX4V.png")
        embed.add_field(name="`r!track_manga [title]`", value="Add manga to personal tracking list", inline=False)
        embed.add_field(name="`r!untrack_manga [title]`", value="Remove manga from tracking list", inline=False)
        embed.add_field(name="`r!untrack_all_manga`", value="Remove all manga from tracking list", inline=False)
        embed.add_field(name="`r!my_manga`", value="Returns a list of tracked manga", inline=False)
        embed.add_field(name="`r!manga [title]`", value="Returns a description and image of a manga", inline=False)
        embed.add_field(name="`r!add_user`", value="Manually add user to the database", inline=False)
        embed.add_field(name="`r!add_guild`", value="Manually add server to the database", inline=False)
        embed.add_field(name="`r!ping`", value="Ping Ruka Bot", inline=False)
        embed.add_field(name="`r!help`", value="Returns a list of commands", inline=False)
        await message.channel.send(embed=embed)

    elif message.content == "r!ping":
        response = "pong"
        await message.channel.send(response) 

nest_asyncio.apply()
db_thread = threading.Thread(target=check_updates)
db_thread.start()
bot.run(TOKEN)

