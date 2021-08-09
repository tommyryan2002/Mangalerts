import datetime
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
import m_requests
import db
import rss
import time
import threading
from datetime import date
from datetime import datetime
import nest_asyncio

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guild_reactions = True
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
bot = commands.Bot(command_prefix='m!', intents = intents, help_command=None)

def check_updates():
    old_data = rss.grab_rss_data()
    while True:
        new_data = rss.grab_rss_data()
        print("Checked RSS" + " " + str(datetime.now().strftime("%H:%M:%S")))
        if new_data != old_data:
            print("New Manga Releases!")
            new_releases = [manga for manga in new_data if manga not in old_data]
            print(new_releases)
            for manga in new_releases:
                asyncio.run_coroutine_threadsafe(notify_users(m_requests.grab_manga_title(manga['title']), manga['chapter'], manga['group']), bot.loop)
        time.sleep(20)
        old_data = new_data

async def notify_users(title: str, chapter: str, group: str):
    if title != "Manga Not Found":
        print(f'Notifying users about: {title}')
        for guild in bot.guilds:
            if db.manga_in_guild(str(guild), title):
                users = db.get_guild_users(str(guild))
                for user_name in users:
                    if db.manga_is_tracked(str(guild), user_name, title) \
                    and db.get_manga_date(str(guild), user_name, title) != date.today().strftime("%m/%d/%Y"):
                        #TODO: Update this code so that instead of searching through every user in the guild, it dirtectly gets the user object by their id, rather than username.
                        for member in guild.members:
                            print(member)
                            if str(member) == user_name:
                                db.modify_date(str(guild), str(member), title, date.today().strftime("%m/%d/%Y"))
                                id = m_requests.grab_manga_id(title)
                                cover = m_requests.grab_cover_id(id)
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


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await bot.change_presence(activity=discord.Game(name="m!help"))
    for guild in bot.guilds:
        print(guild)

@bot.event
async def on_guild_join(guild):
    if not db.guild_in_db(str(guild)):
        try:
            db.add_guild(str(guild))
            response = f"{guild} added to the database!"
        except:
            response = f"Failed to add {guild} to the database"
    else:
        response = f"{guild} already in the database!"
    await guild.channels[0].send(response)

@bot.event
async def on_guild_remove(guild):
    if db.guild_in_db(str(guild)):
        try:
            db.remove_guild(str(guild))
            print(f"{guild} removed from the database!")
        except:
            print(f"Failed to remove {guild} from the database")
    else:
        print(f"{guild} already not in the database!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="manga")
async def manga_desc(ctx):
    string = ctx.message.content
    title = string.replace('m!manga ', '')
    desc_raw = m_requests.grab_manga_description(title)
    title_real = m_requests.grab_manga_title(title)
    ele = desc_raw[0]
    desc= ''
    for ele in desc_raw:
        if ele == '[':
            break
        desc += ele
    id = m_requests.grab_manga_id(title)
    if id is not None:
        cover = m_requests.grab_cover_id(id)
        link = f'https://mangadex.org/title/{id}'
        embed=discord.Embed(title= title_real, url = link, description = desc, color=0xff0000)
        embed.set_author(name='Mangalerts', icon_url='https://imgur.com/nMiqX4V.png')
        embed.set_image(url=f'https://uploads.mangadex.org/covers/{id}/{cover}')
        await ctx.message.channel.send(embed=embed)
    else:
        await ctx.message.channel.send(f"{title} not found on MangaDex!")

@bot.command(name="track_manga")
async def track_manga(ctx):
    if not db.user_in_guild(str(ctx.message.guild), str(ctx.message.author)):
        try:
            db.add_user(str(ctx.message.guild), str(ctx.message.author))
            response1 = f"{ctx.message.author} added to the database!\n"
        except:
            response1 = f"Failed to add {ctx.message.author} to the database"
    else:
        response1 = ''
    string = ctx.message.content
    title = string.replace('m!track_manga ', '')
    real_title = m_requests.grab_manga_title(title)
    if not db.manga_is_tracked(str(ctx.message.guild), str(ctx.message.author), real_title):
        if real_title != "Manga Not Found":
            try:
                db.add_manga(str(ctx.message.guild), str(ctx.message.author), real_title)
                response = f"{ctx.message.author} is now tracking {real_title}!"
            except:
                response = f"Error: {real_title} could not be tracked"
        else:
            response = "Manga Not Found"
    else:
        response = f"{real_title} is already being tracked!"
    await ctx.message.channel.send(response1 + response)

@bot.command(name="untrack_manga")
async def untrack_manga(ctx):
    string = ctx.message.content
    title = string.replace('m!untrack_manga ', '')
    real_title = m_requests.grab_manga_title(title)
    if real_title != "Manga Not Found":
        if db.manga_is_tracked(str(ctx.message.guild), str(ctx.message.author), real_title):
            try:
                db.remove_manga(str(ctx.message.guild), str(ctx.message.author), real_title)
                response = f"{ctx.message.author} is no longer tracking {real_title}!"
            except:
                response = f"Error: {title} could not be untracked"
        else:
            response = f"{title} is already not being tracked"
    else:
        response = f"{title} not found on MangaDex"
    await ctx.send(response)

@bot.command(name="untrack_all_manga")
async def untrack_all_manga(ctx):
    try:
        db.remove_all_manga(str(ctx.message.guild), str(ctx.message.author))
        response = f"{ctx.message.author} is no longer tracking any manga!"
    except:
        response = f"Error: Manga could not be untracked"
    await ctx.send(response)

@bot.command(name="my_manga")
async def my_manga(ctx):
    string = ""
    try:
        manga_list = db.get_user_manga(str(ctx.guild), str(ctx.message.author))
        if len(manga_list) == 0:
            response = f'{ctx.message.author} is not tracking any manga!'
            await ctx.send(response)
        else:
            for manga in manga_list:
                string += '⁠— ' + manga + '\n'
            embed = discord.Embed(title=f"{ctx.message.author}'s Tracked Manga", description=string, color=0xff0000)
            embed.set_author(name= "Mangalerts", icon_url='https://imgur.com/nMiqX4V.png')
            embed.set_thumbnail(url = ctx.message.author.avatar_url)
            await ctx.message.channel.send(embed=embed)
    except:
        response = f'Error: could not retrieve manga for {ctx.message.author}'
        await ctx.send(response)

@bot.command(name="help")
async def help(ctx):
    embed=discord.Embed(title="Mangalerts Commands", color=0xff0000)
    embed.set_author(name="Mangalerts", icon_url="https://imgur.com/nMiqX4V.png")
    embed.add_field(name="`m!track_manga [title]`", value="Add manga to personal tracking list", inline=False)
    embed.add_field(name="`m!untrack_manga [title]`", value="Remove manga from tracking list", inline=False)
    embed.add_field(name="`m!untrack_all_manga`", value="Remove all manga from tracking list", inline=False)
    embed.add_field(name="`m!my_manga`", value="Returns a list of tracked manga", inline=False)
    embed.add_field(name="`m!manga [title]`", value="Returns a description and image of a manga", inline=False)
    embed.add_field(name="`m!ping`", value="Ping Mangalerts", inline=True)
    embed.add_field(name="`m!help`", value="Returns a list of commands", inline=True)
    embed.set_thumbnail(url = 'https://imgur.com/nMiqX4V.png')
    embed.add_field(name = "Still Have an Issue?", value = 'Check out the Mangalerts Github: https://github.com/tommyryan2002/Mangalerts', inline= False)
    embed.add_field(name= "Add Mangalerts to your own server!", value = "https://discord.com/api/oauth2/authorize?client_id=852814525886758922&permissions=0&scope=bot")
    await ctx.send(embed=embed)

nest_asyncio.apply()
db_thread = threading.Thread(target=check_updates)
db_thread.start()
bot.run(TOKEN)

