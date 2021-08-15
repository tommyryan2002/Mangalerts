from discord import user
import pymongo
import os
import json
from pymongo import MongoClient
from pymongo import collection
from dotenv import load_dotenv
from datetime import date
from bson.json_util import dumps
load_dotenv()
DB_PASS = os.getenv('DB_PASS')
cluster = MongoClient(f"mongodb+srv://tpr2:{DB_PASS}@rukadb.jbzul.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster['Ruka']
col = db["guilds"]

def add_guild(guild_name: str):
    document_count = col.count_documents({})
    while document_count >= 0:
        try:
            col.insert_one({'_id': document_count, 'guild_name': guild_name, 'users': []})
        except:
            document_count -= 1
    


def remove_guild(guild_name:str):
    col.delete_one({'guild_name': guild_name})

def add_user(guild_name: str, username: str):
    if guild_in_db(guild_name):
        col.update_one({'guild_name': guild_name}, { '$push': {"users": {"name": username, "manga": []}}})
    else:
        raise RuntimeError

def add_manga(guild_name: str, username: str, manga_title: str):
    col.update_one({'guild_name': guild_name, "users.name" : username}, { '$push': {"users.$.manga": {"title": manga_title, "date": date.today().strftime("%m/%d/%Y")}}})

def remove_manga(guild_name: str, username: str, manga_title: str):
    col.update_one({'guild_name': guild_name, "users.name" : username}, { '$pull': {"users.$.manga": {"title": manga_title}}})

def remove_all_manga(guild_name: str, username: str):
    col.update_many({'guild_name': guild_name, "users.name" : username}, { '$set': {"users.$.manga": []}})

def user_in_guild(guild_name: str, username: str) -> bool:
    result = col.find_one({'guild_name': guild_name, 'users.name': username})
    return result != None

def guild_in_db(guild_name: str) -> bool:
    result = col.find_one({'guild_name': guild_name})
    return result != None

def get_user_manga(guild_name: str, username: str):
    results = col.aggregate([{'$match':{'guild_name': guild_name}}, \
        {'$unwind': "$users"}, {"$match": {'users.name': username}}, \
            {'$unwind': '$users.manga'}])
    results = json.loads(dumps(results))
    manga = [ele['users']['manga']['title'] for ele in results]
    return manga

def manga_is_tracked(guild_name: str, username: str, manga_title: str) -> bool:
    result = col.find_one({'guild_name': guild_name, 'users': {'$elemMatch': {"name": username, 'manga': {'$elemMatch': {"title": manga_title}}}}})
    return result != None

def manga_in_guild(guild_name: str, title: str) -> bool:
    results = col.find({'guild_name': guild_name, 'users.manga': {'$elemMatch': {'title': title}}}, {'_id': 0, "guild_name": 0})
    r = []
    for result in results:
        r.append(result)
    return r != []

def get_all_guilds():
    results = col.find({}, {'users': 0})
    r = []
    for result in results:
        r.append(result['guild_name'])
    return r

def get_guild_users(guild_name: str):
    results = col.find({'guild_name': guild_name}, {"guild_name": 0, "_id": 0})
    r = []
    for result in results:
        for user in result['users']:
            r.append(user['name'])
    return r

def modify_date(guild_name: str, username: str, manga_title: str, date: str):
    col.update_one({'guild_name': guild_name, 'users.name': username, 'users.manga': {'$elemMatch': {'title': manga_title}}}, \
        {'$set': {'users.$.manga.$[ele].date': date}}, False, array_filters= [{'ele.title': manga_title}])


def get_manga_date(guild_name: str, username: str, manga_title: str):
    results = col.aggregate([{'$match':{'guild_name': guild_name}}, \
        {'$unwind': "$users"}, {"$match": {'users.name': username}}, \
            {'$unwind': '$users.manga'}, {'$match': {"users.manga.title": manga_title}}])
    json_data = json.loads(dumps(results))
    return json_data[0]['users']['manga']['date']