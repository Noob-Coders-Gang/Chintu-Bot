import discord
from discord.ext import commands
from itertools import cycle

class Loops:
    def __init__(self, bot:commands.Bot, custom_statuses):
        self.bot = bot
        self.custom_statuses = custom_statuses

    async def change_status(self):
        """Task loop for changing bot statuses"""
        await self.bot.change_presence(activity=discord.Game(next(cycle(self.custom_statuses))))