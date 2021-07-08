import math

import asyncio
import os
import re

import discord
from discord.ext import commands

from main import database
from main_resources.functions import *

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

    def __init__(self, bot: commands.Bot):
        self.emojis = None
        self.bot = bot
        self.count = 0
        self.cmd_list = []
        for cmd in bot.commands:
            # Get all commands registered with the bot
            self.cmd_list.append(cmd.name)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Sends the latency of the bot"""
        em = discord.Embed(title='Latency', description='🏓Pong {0}'.format(math.trunc(self.bot.latency * 1000)) + 'ms',
                           color=discord.Color(0x4293f5))
        await ctx.send(embed=em)

    @commands.command(name="suggest")
    async def suggest(self, ctx: discord.ext.commands.Context, *, suggestion: str):
        """Suggest a feature or an improvement for chintu!"""
        em = discord.Embed(
            title="Your suggestion has been recorded!", color=discord.Color.green())
        sugg_em = discord.Embed(
            title=f"Suggestion from {ctx.author.name}#{ctx.author.discriminator}", description=suggestion)
        await self.bot.get_channel(813268502839820318).send(embed=sugg_em)
        await ctx.send(embed=em)

    @commands.command(name="invite")
    async def invite(self, ctx):
        """Invite Chintu to your server!!!"""
        await ctx.send(
            "https://discord.com/oauth2/authorize?client_id=790900950885203978&permissions=2026368118&scope=bot")

    @commands.command(name="prefix", aliases=["changeprefix"])
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix: str):
        """Change Chintu's prefix (Use double quotes [" "] around the prefix to add whitespace [$prefix "pls "])"""
        update_prefix(database["guilds_data"], ctx.guild.id, prefix)
        self.bot.dispatch("update_prefix", ctx, prefix)
        embed = discord.Embed(title=f"The prefix of your guild was changed to {prefix}",
                              color=discord.Colour.green())
        await ctx.send(embed=embed)

    @commands.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, command_name: str):
        """Add a previously removed command back to your server"""
        if command_name in self.cmd_list:
            remove_cmd_from_collection(database["guilds_data"], ctx.guild.id, command_name, os.getenv("PREFIX"))
            self.bot.dispatch("add_command", ctx, command_name)
            embed = discord.Embed(title=f"I have added the {command_name} command back to your server!",
                                  color=discord.Colour.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, command_name: str):
        """Remove a command from your server"""
        if command_name in self.cmd_list:
            add_cmd_to_collection(database["guilds_data"], ctx.guild.id, command_name, os.getenv("PREFIX"))
            self.bot.dispatch("remove_command", ctx, command_name)
            embed = discord.Embed(title=f"I have removed the {command_name} command from your server!",
                                  color=discord.Colour.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command(name="formemb", hidden=True)
    @commands.is_owner()
    async def formemb(self, ctx: commands.Context, channel: discord.TextChannel, *, title):
        """Create embed for announcement and stuff"""
        try:
            await ctx.send("Send description")

            def check(message):
                return message.channel == ctx.channel and message.author.id == ctx.author.id

            msg = await self.bot.wait_for('message', timeout=90.0, check=check)
            if msg.content.lower() != "none":
                emb = discord.Embed(title=title, description=msg.content)
            else:
                emb = discord.Embed(title=title)
            while True:
                await ctx.send("Add `field name` or `done` to send or `cancel` to cancel")
                msg = await self.bot.wait_for('message', timeout=90.0, check=check)
                if msg.content.lower() == "cancel":
                    await ctx.send("Cancelled")
                    return
                if msg.content.lower() == "done":
                    await channel.send(embed=emb)
                    await ctx.send("Done")
                    return
                name = msg.content
                await ctx.send("Add `field value` and add `inline` to set to True")
                msg = await self.bot.wait_for('message', timeout=90.0, check=check)
                if "inline" in msg.content.lower():
                    value = msg.content.replace("inline", "")
                    emb.add_field(name=name, value=value, inline=True)
                else:
                    value = msg.content
                    emb.add_field(name=name, value=value, inline=False)

        except asyncio.TimeoutError:
            await ctx.send("Cancelled")
            return

    def get_emoji(self, match):
        try:
            return self.emojis[str(match.group()).replace(":", "")]
        except KeyError:
            return str(match.group())

    @commands.command(name="nitro", aliases=["n"])
    async def nitro(self, ctx: commands.Context, *, message):
        """Use any emote that Chintu has access to in your message!"""
        sent = False
        if self.emojis is None:
            self.emojis = {e.name.lower(): str(e) for e in self.bot.emojis}
        message = re.sub(r':[^:]+:', self.get_emoji, message, count=0)
        webhooks = await ctx.channel.webhooks()
        if len(webhooks) > 0:
            for webhook in webhooks:
                try:
                    await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)
                    sent = True
                    break
                except discord.errors.InvalidArgument:
                    continue
            if not sent:
                webhook = await ctx.channel.create_webhook(name=self.bot.user.name)
                await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)
        else:
            webhook = await ctx.channel.create_webhook(name=ctx.author.name)
            await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)


def setup(bot):
    bot.add_cog(Utility(bot))
