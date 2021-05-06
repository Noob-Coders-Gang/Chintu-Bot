import os

from discord import Intents
from discord.ext import commands, tasks
from dotenv import load_dotenv

from main_resources.events import Events
from main_resources.functions import create_database_connection, update_cmdManager_coll
from main_resources.loops import Loops

# --------------------------------Variables--------------------------------#
load_dotenv()
intents = Intents.all()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='BB', help_command=None, case_insensitive=True, intents=intents)
custom_statuses = ['$help', 'WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']

# The url for updating server count.
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')
database = create_database_connection(os.getenv('MONGODB_URL'))
cmdManager_collection = database["cmd_manager"]


# --------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    print("updating databases...")
    update_cmdManager_coll(bot, database)
    print('Logged in as {0.user}'.format(bot))


# --------------------------------Task loops--------------------------------#

loops = Loops(bot, custom_statuses)
change_status = tasks.loop(seconds=60)(loops.change_status)

# --------------------------------Events--------------------------------#
events = Events(bot, database, total_guilds_api_url, ChintuAI=False)
bot.event(events.on_command_error)
bot.event(events.on_message)
bot.event(events.on_guild_join)


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
    print("loading extensions...")
    load_extensions(bot, ["manage_commands.py", "Help.py", "Memes.py"])
    bot.load_extension("cogs.manage_commands")
    bot.load_extension("cogs.Help")
    print("logging in...")
    bot.run(os.getenv("TOKEN"))
