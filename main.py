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
bot = commands.Bot(command_prefix='$')
custom_statuses = ['WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')  # The url for updating server count.
database = create_database_connection(os.getenv('MONGODB_URL'))
cmdManager_collection = database["cmd_manager"]
total_guilds_api_url = os.getenv("TOTAL_GUILDS_API_URI")

#--------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    print("Updating databases....")
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


load_extensions(bot, ["manage_commands.py"])
bot.load_extension("cogs.manage_commands")
bot.run(os.getenv("TOKEN"))
