import os

import discord
import pymongo
import requests
from discord.ext.commands import CommandError


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


def update_guilds_data(bot, collection, default_prefix):
    guilds_to_add = []
    current_guilds = list(
        collection.find({}, {"_id": 1}))  # Get the list of already registered guilds
    for guild in bot.guilds:
        if {"_id": guild.id} not in current_guilds:
            guilds_to_add.append(
                {"_id": guild.id, "disabled_commands": [],
                 "prefix": default_prefix})  # Add all the guilds that are not registered to a list
    if len(guilds_to_add) > 0:
        collection.insert_many(guilds_to_add)  # update the collection with the list


def add_guild(collection, guild_id: int, default_prefix):
    collection.update_one({"_id": guild_id}, {
        "$setOnInsert": {
            "disabled_commands": [],
            "prefix": default_prefix
        }
    }, upsert=True)


def update_guild_storage(guild_store, guild_id, prefix):
    guild_store[guild_id] = prefix


def add_disabled_command(disabled_commands_store, guild_id, disabled_command):
    disabled_commands_store[guild_id].append(disabled_command)


def remove_disabled_command(disabled_commands_store: dict, guild_id, enabled_command):
    disabled_commands_store[guild_id].remove(enabled_command)


def create_guild_store(collection):
    guild_store = {}
    for document in collection.find({}, {"_id": 1, "prefix": 1}):
        guild_store[document["_id"]] = document["prefix"]
    return guild_store


def create_disabled_commands_store(collection):
    guild_store = {}
    for document in collection.find({}, {"_id": 1, "disabled_commands": 1}):
        guild_store[document["_id"]] = document["disabled_commands"]
    return guild_store


def update_prefix(collection, server_id, prefix):
    collection.update_one({"_id": server_id}, {
        "$set": {"prefix": prefix},
        "$setOnInsert": {"disabled_commands": []}
    }, upsert=True)


def add_cmd_to_collection(collection, server_id, disabled_command, default_prefix):
    collection.update_one({"_id": server_id}, {
        "$addToSet": {"disabled_commands": disabled_command},
        "$setOnInsert": {"prefix": default_prefix}
    }, upsert=True)


def remove_cmd_from_collection(collection, server_id, disabled_command, default_prefix):
    collection.update_one({"_id": server_id}, {
        "$pull": {"disabled_commands": disabled_command},
        "$setOnInsert": {"prefix": default_prefix}
    }, upsert=True)


class before_invoke:
    def __init__(self, disabled_commands):
        self.disabled_commands = disabled_commands

    async def check_before_invoke(self, ctx):
        command_name = ctx.command.name
        if command_name != "add":
            try:
                if command_name in self.disabled_commands[ctx.guild.id]:
                    embed = discord.Embed(title=f"This command is disabled in your server!",
                                          color=discord.Colour.red())
                    await ctx.send(embed=embed)
                    raise CommandError
            except KeyError:
                self.disabled_commands[ctx.guild.id] = []
