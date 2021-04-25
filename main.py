import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print("Hello World!")


load_dotenv()
bot.run(os.getenv("TOKEN"))
