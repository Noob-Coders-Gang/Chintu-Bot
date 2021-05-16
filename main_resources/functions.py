import os

import pymongo
import requests

from main import guild_storage

def update_total_guilds(guild_list, total_guilds_api_url):
    """Update the number of guilds in the total guilds API"""
    headers = {'Content-Type': 'application/json'}
    data = {"total_servers": len(guild_list)}
    requests.put(total_guilds_api_url, json=data, headers=headers)


def load_extensions(bot, unloaded_cogs=None):
    """Loads all extensions (Cogs) from the cogs directory"""
    if unloaded_cogs is None:
        unloaded_cogs = []
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            if filename not in unloaded_cogs:
                bot.load_extension(f'cogs.{filename[:-3]}')


# Database functions
def create_database_connection(mongo_db_url: str):
    client = pymongo.MongoClient(mongo_db_url)  # Connect to MongoDB using URI in .env file
    return client["Chintu-Bot"]  # Return the Chintu-Bot database


def update_cmdManager_coll(bot, database):
    guilds_to_add = []
    cmdManager_collection = database["cmd_manager"]  # Get the cmd_manager collection
    current_guilds = list(
        cmdManager_collection.find({}, {"_id": 1, "disabled_commands": 0}))  # Get the list of already registered guilds
    for guild in bot.guilds:
        if {"_id": guild.id} not in current_guilds:
            guilds_to_add.append(
                {"_id": guild.id, "disabled_commands": []})  # Add all the guilds that are not registered to a list
    if len(guilds_to_add) > 0:
        cmdManager_collection.insert_many(guilds_to_add)  # update the collection with the list


def add_guild(bot, database, guild):
    cmdManager_collection = database["cmd_manager"]
    current_guilds = list(cmdManager_collection.find({}, {"_id": 1, "disabled_commands": 0}))
    if {"_id": guild.id} not in current_guilds:
        cmdManager_collection.insert({"_id": guild.id, "disabled_commands": []})
    
    bot_util_collection = database['bot_util']
    guilds = list(bot_util_collection.find({}, {"_id": 1, "prefix": 0}))
    if {"_id": guild.id} not in guilds:
        bot_util_collection.insert({"_id": guild.id, "prefix": os.getenv('PREFIX')})

def update_guild_storage(database):
    global guild_storage
    bot_util_collection = database['bot_util']
    guild_storage.clear()
    guild_storage.append(list(bot_util_collection.find({}, {"_id": 1, "prefix": 0})))

def update_prefix(database,server_id, prefix):
    bot_util_collection = database['bot_util']
    bot_util_collection.insert({"_id": server_id, "prefix": prefix})