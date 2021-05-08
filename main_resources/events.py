import discord
from discord.ext import commands

from main_resources.ChintuAI import AskChintu
from main_resources.functions import update_total_guilds, add_guild


class Events:
    def __init__(self, bot: commands.Bot, database, total_guilds_api_url, ChintuAI: bool = False):
        self.bot = bot
        self.database = database
        self.cmdManager_collection = database["cmd_manager"]
        self.total_guilds_api_url = total_guilds_api_url
        self.ChintuAI = ChintuAI
        if ChintuAI:
            pass

    async def on_guild_join(self, guild: discord.Guild):
        guilds = self.bot.guilds
        update_total_guilds(guilds, self.total_guilds_api_url)
        add_guild(self.bot, self.database, guild)

    async def on_message(self, message: discord.Message):
        if self.ChintuAI:
            if message.author == self.bot:
                return
            mention = f'<@!{self.bot.user.id}>'
            if self.bot.user.mentioned_in(message):
                user_message = message.content.replace(mention, "")
                await message.channel.send(AskChintu(user_message)['response'])
        if message.content.startswith(self.bot.command_prefix):
            cmd = message.content.replace(self.bot.command_prefix, "").split()[
                0]  # Strip the command from the message
            try:
                disabled_commands = self.cmdManager_collection.find_one({"_id": message.guild.id})[
                    "disabled_commands"]  # Get disabled commands for the specific guild
            except Exception:
                disabled_commands = []
                pass
            if cmd in disabled_commands:  # Deny processing
                embed = discord.Embed(title=f"This command is disabled in your server!",
                                      color=discord.Colour.red())
                await message.channel.send(embed=embed)
            else:  # Process the command
                await self.bot.process_commands(message)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title=f"Slow it down bro!",
                               description=f"Try again in {error.retry_after:.2f}s.", color=discord.Color.red())
            await ctx.send(embed=em)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(title=':x: oops! You do not have permission to use this command.',
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=':x: You are missing the required arguments. Please check if your command requires an addition arguement.',
                color=discord.Colour.red())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title=':x: Chintu is missing the required permissions. Please check if Chintu has appropriate permissions.',
                color=discord.Colour.red())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title=':x: Could not find the mentioned user. Please mention a valid user.',
                color=discord.Colour.red())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title=':x: Enter a valid argument',
                color=discord.Colour.red())
            await ctx.send(embed=embed)
