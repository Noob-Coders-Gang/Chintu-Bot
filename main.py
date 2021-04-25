import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
from itertools import cycle

load_dotenv()
bot = commands.Bot(command_prefix='$')

#--------------------------------Variables--------------------------------#
custom_statuses = ['WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')  # The url for updating server count.


#--------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    print('Logged in as {0.user}'.format(bot))


#--------------------------------Task loops--------------------------------#
@tasks.loop(seconds=300)
async def change_status():
    """Task loop for changing bot statuses"""
    await bot.change_presence(activity=discord.Game(next(cycle(custom_statuses))))


#--------------------------------Events--------------------------------#
@bot.event
async def on_guild_join(guild:discord.Guild):
    guilds = bot.guilds
    update_total_guilds(guilds)


# Error handler
@bot.event
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: oops! You do not have permission to use this command.',
                              color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=':x:You are missing the required arguments. Please check if your command requires an addition arguement.',
            color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=':x:Chintu is missing the required permissions. Please check if Chintu has appropriate permissions.',
            color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass


#--------------------------------Funtions--------------------------------#
def update_total_guilds(guild_list):
    """Update the number of guilds in the total guilds API"""
    headers = {'Content-Type': 'application/json'}
    data = {"total_servers": len(guild_list)}
    requests.put(total_guilds_api_url, json=data, headers=headers)


def load_extensions():
    """Loads all extensions (Cogs) from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            if filename not in ["Subs.py"]:
                bot.load_extension(f'cogs.{filename[:-3]}')


load_extensions()
bot.run(os.getenv("TOKEN"))
