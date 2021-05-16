import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from main_resources.events import Events
from main_resources.functions import create_database_connection, update_cmdManager_coll
from main_resources.loops import Loops

# --------------------------------Variables--------------------------------#

load_dotenv()  #Load env to initialize all dataset

# The url for updating server count.
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')
database = create_database_connection(os.getenv('MONGODB_URL'))
cmdManager_collection = database["cmd_manager"]
bot_util_collection = database['bot_util']
guild_storage = list(bot_util_collection.find({}, {"_id": 1, "prefix": 0}))

# ---------------------------------Prefix----------------------------------#

DEFAULT_PREFIX = os.getenv('PREFIX')

#Get prefix per server
def get_prefix(bot, message):
    global guild_storage
    if not guild_storage:
        guild_storage = list(bot_util_collection.find({}, {"_id": 1, "prefix": 0}))
    id = message.server.id
    if id in guild_storage:
        prefix = bot_util_collection.find_one({"_id": id}, {"prefix": 1})
        return str(prefix)
    return DEFAULT_PREFIX

# -----------------------------------Bot-----------------------------------#

bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True, intent=discord.Intents().all())
custom_statuses = [f'{DEFAULT_PREFIX}help', 'WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']

# --------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    print("Updating databases...")
    update_cmdManager_coll(bot, database)
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} ID = {bot.user.id}')


# --------------------------------Task loops--------------------------------#

loops = Loops(bot, custom_statuses)
change_status = tasks.loop(seconds=60)(loops.change_status)

# --------------------------------Events--------------------------------#
events = Events(bot, database, total_guilds_api_url, ["help", "kick", "ban", "warn", "warninfo", "warns", "mute", "unmute", "clear"],
                ChintuAI=True)
bot.event(events.on_command_error)
bot.event(events.on_message)
bot.event(events.on_guild_join)
bot.event(events.on_command_completion)


# --------------------------------Load Extensions/cogs--------------------------------#
def load_extensions(fun_bot, unloaded_cogs: list):
    """Loads all extensions (Cogs) from the cogs directory"""
    if unloaded_cogs is None:
        unloaded_cogs = []
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            if filename not in unloaded_cogs:
                fun_bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
    print("Loading extensions...")
    load_extensions(bot, ["manage_commands.py", "Help.py"])
    bot.load_extension("cogs.manage_commands")
    bot.load_extension("cogs.Help")
    print("Logging in...")
    bot.run(os.getenv("TOKEN"))
