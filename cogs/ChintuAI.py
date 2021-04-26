import discord
import requests
from discord.ext import commands


class ChintuAI(commands.Cog):
    def __init__(self, commands):
        self.commands = commands

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')


def setup(bot):
    bot.add_cog(ChintuAI(bot))
