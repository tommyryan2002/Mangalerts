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

import pymongo
import os
from pymongo import MongoClient
from pymongo import collection
from dotenv import load_dotenv
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
    col.update_one({'guild_name': guild_name, f"users.name" : username}, { '$push': {"users.$.manga": {manga_title: {}}}})

add_guild("Los Amigos :)")


