#comments
    #adding
    #a post is an 'entry', look like json files, have _id tag that is used to access it
    #creating a post creates dictionary keys that map to values
    #col.insert_one({'_id': 0, "guild_names": "THE FREEZER"})

    #find/query
    #results = col.find({"guild_names":"THE FREEZER"})
    #print(results)
    #for result in results:
        #print(result["guild_names"])

    #deleting
    #r = col.delete_one({"_id":0})

import re
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
    col.insert_one({'_id': document_count, 'guild_name': guild_name, 'users': []})

def add_user(guild_name: str, username: str):
    col.update_one({'guild_name': guild_name}, { '$push': {"users": {"name": username, "manga": []}}})

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

def manga_is_tracked(guild_name: str, username: str, manga_title: str) -> bool:
    result = col.find_one({'guild_name': guild_name, 'users': {'$elemMatch': {"name": username, 'manga': {'$elemMatch': {"title": manga_title}}}}})
    return result

def get_user_manga(guild_name: str, username: str):
    filter1 = {'guild_name': guild_name, 'users': {'$elemMatch': {"name": username}}}
    filter2 = {'_id': 0, 'guild_name': 0, 'users.name': 0}
    manga_json = col.find_one(filter1, filter2)['users'][0]['manga']
    return [ele['title'] for ele in manga_json]

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

def get_manga_date(guild_name: str, username: str, manga_title: str):
    results = col.aggregate([{'$match':{'guild_name': guild_name}}, \
        {'$unwind': "$users"}, {"$match": {'users.name': username}}, \
            {'$unwind': '$users.manga'}, {'$match': {"users.manga.title": manga_title}}])
    json_data = json.loads(dumps(results))
    return json_data[0]['users']['manga']['date']
print(manga_is_tracked("Los Amigos :)", "idkwho?#7464", "Jujutsu Kaisen"))