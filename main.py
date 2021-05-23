import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from main_resources.events import Events
from main_resources.functions import *
from main_resources.loops import Loops

# --------------------------------Variables--------------------------------#

load_dotenv()  # Load env to initialize all dataset

# The url for updating server count.
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')
database = create_database_connection(os.getenv('MONGODB_URL'))
guilds_data = database['guilds_data']
guild_prefix_storage = create_guild_store(guilds_data)
disabled_commands_store = create_disabled_commands_store(guilds_data)
# ---------------------------------Prefix----------------------------------#

DEFAULT_PREFIX = os.getenv('PREFIX')


# Get prefix per server
def get_prefix(bot, message: discord.Message):
    guild_id = message.guild.id
    if guild_id in guild_prefix_storage:
        return guild_prefix_storage[guild_id]
    else:
        add_guild(guilds_data, guild_id, DEFAULT_PREFIX)
        return DEFAULT_PREFIX


# -----------------------------------Bot-----------------------------------#

bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)
custom_statuses = [f'{DEFAULT_PREFIX}help', 'WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']
check_class = before_invoke(disabled_commands_store)
bot.before_invoke(check_class.check_before_invoke)


# --------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    clear_game.start()
    print("Updating databases...")
    update_guilds_data(bot, guilds_data, DEFAULT_PREFIX)
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} ID = {bot.user.id}')

# --------------------------------Task loops--------------------------------#

loops = Loops(bot, custom_statuses)
change_status = tasks.loop(seconds=60)(loops.change_status)
clear_game = tasks.loop(seconds=10)(loops.clear_game)

# --------------------------------Events--------------------------------#
events = Events(bot, database, total_guilds_api_url, guild_prefix_storage, disabled_commands_store, DEFAULT_PREFIX,
                ["help", "kick", "ban", "warn", "warninfo", "warns", "mute", "unmute", "clear"],
                ChintuAI=True)
bot.event(events.on_command_error)
bot.event(events.on_message)
bot.event(events.on_guild_join)
bot.event(events.on_command_completion)
bot.event(events.on_update_prefix)
bot.event(events.on_add_command)
bot.event(events.on_remove_command)
bot.event(events.on_reaction_add)


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
    load_extensions(bot, ["Utilities.py", "Help.py"])
    bot.load_extension("cogs.Utilities")
    bot.load_extension("cogs.Help")
    print("Logging in...")
    bot.run(os.getenv("TOKEN"))
