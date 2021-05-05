import math

import discord
from discord.ext import commands

intervals = (
    ('years', 604800 * 52),
    ('months', 604800 * 4),
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


class Utility(commands.Cog):
    ''' Utility Commands '''

    def __init__(self, bot):
        self.bot = bot
        self.count = 0

    @commands.command()
    async def ping(self, ctx):
        """Sends the latency of the bot"""
        em = discord.Embed(title='Latency', description='🏓Pong {0}'.format(math.trunc(self.bot.latency * 1000)) + 'ms',
                           color=discord.Color(0x4293f5))
        await ctx.send(embed=em)

    @commands.command()
    async def suggest(self, ctx: discord.ext.commands.Context, *, suggestion: str):
        """Suggest a feature or an improvement for chintu!"""
        em = discord.Embed(
            title="Your suggestion has been recorded!", color=discord.Color.green())
        sugg_em = discord.Embed(
            title=f"Suggestion from {ctx.author.name}#{ctx.author.discriminator}", description=suggestion)
        await self.bot.get_channel(813268502839820318).send(embed=sugg_em)
        await ctx.send(embed=em)

    @commands.command()
    async def invite(self, ctx):
        """Invite Chintu to your server!!!"""
        await ctx.send(
            "https://discord.com/oauth2/authorize?client_id=790900950885203978&permissions=2026368118&scope=bot")


def setup(bot):
    bot.add_cog(Utility(bot))
