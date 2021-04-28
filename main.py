import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
from itertools import cycle


import pymongo
from main_resources.events import Events
from main_resources.functions import load_extensions, create_database_connection, update_cmdManager_coll
from main_resources.loops import Loops

#--------------------------------Variables--------------------------------#
load_dotenv()
bot = commands.Bot(command_prefix='$', help_command=None)
custom_statuses = ['WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']

# The url for updating server count.
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')
database = create_database_connection(os.getenv('MONGODB_URL'))
cmdManager_collection = database["cmd_manager"]


#--------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    update_cmdManager_coll(bot, database)
    print('Logged in as {0.user}'.format(bot))


#--------------------------------Task loops--------------------------------#

loops = Loops(bot, custom_statuses)
change_status = tasks.loop(seconds=300)(loops.change_status)


#--------------------------------Events--------------------------------#
events = Events(bot, database, total_guilds_api_url)
bot.event(events.on_command_error)
bot.event(events.on_message)
bot.event(events.on_guild_join)


#--------------------------------Funtions--------------------------------#
def load_extensions(bot, unloaded_cogs=[]):
    """Loads all extensions (Cogs) from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            if filename not in unloaded_cogs:
                bot.load_extension(f'cogs.{filename[:-3]}')


load_extensions(bot, ["manage_commands.py"])
bot.run(os.getenv("TOKEN"))
