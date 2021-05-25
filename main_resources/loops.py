import discord
from discord.ext import commands
from itertools import cycle
from cogs.utils import GameGrid
from main import database
from cogs.currency_utils.utils import currency_utils


class Loops:
    def __init__(self, bot: commands.Bot, custom_statuses):
        self.bot = bot
        self.custom_statuses = custom_statuses
        self.collection = database["currency"]
        self.utils = currency_utils(self.collection)

    async def change_status(self):
        """Task loop for changing bot statuses"""
        await self.bot.change_presence(activity=discord.Game(next(cycle(self.custom_statuses))))
    
    async def clear_game(self):
        """Task loop for clearing 2048 games"""

        for game in GameGrid.getGames():
            if game.getLastUpdate() > 60.0:
                msg = game.getEmojiMessage()
                point = game.getPoint()
                coins = int(point / 2)
                channel = self.bot.get_channel(int(game.getChannelId()))
                # user = self.bot.get_user(int(game.getId()))
                game.stop()
                embed = discord.Embed(title="2048 Game Over!", 
                                        description=f"**Points:** {point}\n**Coins:** {coins}\n\n{msg}", 
                                        color=discord.Color.orange())
                embed.set_footer(text=f'Game session of {game.name}', icon_url=game.url)
                self.utils.update_and_insert(int(game.getId()), inc_vals={"wallet": coins}, wallet=False)
                await channel.send(embed=embed)
