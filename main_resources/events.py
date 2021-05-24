import discord
from discord.ext import commands
from discord.ext.commands import CommandError

from cogs.currency_utils.utils import currency_utils
from cogs.utils import GameGrid
from main_resources.ChintuAI import AskChintu
from main_resources.functions import *


class Events:
    def __init__(self, bot: commands.Bot, database, total_guilds_api_url, guild_prefix_store, disabled_commands,
                 default_prefix, infinite_use_commands: list,
                 ChintuAI: bool = False):
        self.bot = bot
        self.database = database
        self.infinite_use_commands = infinite_use_commands
        self.total_guilds_api_url = total_guilds_api_url
        self.utils = currency_utils(database["currency"])
        self.guilds_data = database["guilds_data"]
        self.ChintuAI = ChintuAI
        self.guild_prefix_store = guild_prefix_store
        self.default_prefix = default_prefix
        self.disabled_commands = disabled_commands
        if ChintuAI:
            from main_resources.ChintuAI import AskChintu

    async def on_guild_join(self, guild: discord.Guild):
        guilds = self.bot.guilds
        update_total_guilds(guilds, self.total_guilds_api_url)
        add_guild(self.guilds_data, guild.id, self.default_prefix)
        update_guild_storage(self.guild_prefix_store, guild.id, self.default_prefix)

    async def on_message(self, message: discord.Message):
        message.content = message.content.lower()
        ctx: commands.Context = await self.bot.get_context(message)
        if ctx.command is None:
            if message.content.startswith("$help"):
                await ctx.invoke(self.bot.get_command("invoked_help"))
            elif self.ChintuAI:
                if message.author == self.bot or message.content.startswith(self.default_prefix):
                    return
                mention = f'<@!{self.bot.user.id}>'
                if self.bot.user.mentioned_in(message):
                    user_message = message.content.replace(mention, "")
                    await message.channel.send(AskChintu(user_message)['response'])
        else:
            await self.bot.invoke(ctx)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title=f"Slow it down bro!",
                               description=f"Try again in {error.retry_after:.2f}s.\n The default cooldown is {error.cooldown.per}s",
                               color=discord.Color.red())
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

    async def on_command_completion(self, ctx: commands.Context):
        if ctx.command.name not in self.infinite_use_commands:
            self.utils.update_and_insert(ctx.author.id, inc_vals={"commands": 1}, commands=False)

    async def on_update_prefix(self, ctx, prefix):
        update_guild_storage(self.guild_prefix_store, ctx.guild.id, prefix)
        await ctx.guild.me.edit(nick=self.bot.user.name.replace(self.default_prefix, prefix))

    async def on_add_command(self, ctx, command_name):
        try:
            remove_disabled_command(self.disabled_commands, ctx.guild.id, command_name)
        except ValueError:
            pass

    async def on_remove_command(self, ctx, command_name):
        try:
            add_disabled_command(self.disabled_commands, ctx.guild.id, command_name)
        except ValueError:
            pass

    async def on_reaction_add(self, reaction, user):
        if user.id == self.bot.user.id:
            return

        message = reaction.message

        if GameGrid.getGamesByUser(str(user.id)) is not None:
            game = GameGrid.getGamesByUser(str(user.id))
            if str(game.getMessageId()) == str(message.id):
                if str(reaction.emoji) == '⬆':
                    prev = game.getEmojiMessage()
                    game.slideUp()
                elif str(reaction.emoji) == '⬇':
                    prev = game.getEmojiMessage()
                    game.slideDown()
                elif str(reaction.emoji) == '➡':
                    prev = game.getEmojiMessage()
                    game.slideRight()
                elif str(reaction.emoji) == '⬅':
                    prev = game.getEmojiMessage()
                    game.slideLeft()
                elif str(reaction.emoji) == '❌':
                    msg = game.getEmojiMessage()
                    point = game.getPoint()
                    game.stop()
                    await message.delete()
                    embed = discord.Embed(title="2048 Game Over!", 
                                          description=f"Points: {point}\n\n{msg}", 
                                          color=discord.Color.orange())
                    embed.set_footer(text=f'Game session of {user.name}', icon_url=user.avatar_url)
                    await message.channel.send(embed=embed)
                    return

                await message.remove_reaction(reaction, user)

                if prev == game.getEmojiMessage():
                    return
                game.randomNumber()
                game.updatePoint(1)
                msg = game.getEmojiMessage()

                await message.edit(content=msg)

                if game.isGameWon():
                    asyncio.sleep(5)
                    msg = game.getEmojiMessage()
                    point = game.getPoint()
                    game.stop()
                    await message.delete()
                    embed = discord.Embed(title="Congratulations!", 
                                          description=f"You won the game!\nPoints: {point}\n\n{msg}", 
                                          color=discord.Color.green())
                    embed.set_footer(text=f'Game session of {user.name}', icon_url=user.avatar_url)
                    await message.channel.send(embed=embed)
                    return

                if game.isGameOver():
                    asyncio.sleep(5)
                    msg = game.getEmojiMessage()
                    point = game.getPoint()
                    game.stop()
                    await message.delete()
                    embed = discord.Embed(title="2048 Game Over!", 
                                          description=f"Points: {point}\n\n{msg}", 
                                          color=discord.Color.orange())
                    embed.set_footer(text=f'Game session of {user.name}', icon_url=user.avatar_url)
                    await message.channel.send(embed=embed)
                    return