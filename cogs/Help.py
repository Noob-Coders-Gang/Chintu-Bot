import discord
from discord.errors import Forbidden
from discord.ext import commands
from main import guild_prefix_storage, database, DEFAULT_PREFIX
from main_resources.functions import *


async def send_embed(ctx, embed):
    """
        function to send the embed in dm in the case of bot don't have permission to send message in particular channel
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


def prebuild_embed(bot):
    # starting to build embed

    # ------------------- iterating trough cogs, gathering descriptions------------------#

    cogs_desc = ''
    for cog in bot.cogs:
        cogs_desc += f'`{cog}` {bot.cogs[cog].__doc__}\n'

    # ------------------- Adding all cogs to Help embed ------------------#

    # integrating trough uncategorized commands
    commands_desc = ''
    for command in bot.walk_commands():
        # if cog not in a cog
        # listing command if cog name is None and command isn't hidden
        if not command.cog_name and not command.hidden:
            commands_desc += f'{command.name} - {command.help}\n'

    return cogs_desc, commands_desc


def get_prefix(bot, message: discord.Message):
    guild_id = message.guild.id
    if guild_id in guild_prefix_storage:
        return guild_prefix_storage[guild_id]
    else:
        add_guild(database["guilds_data"], guild_id, DEFAULT_PREFIX)
        return DEFAULT_PREFIX


class Help(commands.Cog):
    """ Sends this help message """

    def __init__(self, bot):
        self.bot = bot
        cogs = {}
        for cog in bot.cogs:
            cogs[cog.lower()] = cog
        self.cogs = cogs
        bot_commands = {}
        for command in bot.walk_commands():
            bot_commands[command.name] = command
        self.cogs_desc, self.commands_desc = prebuild_embed(bot)
        self.bot_commands = bot_commands

    @commands.command()
    async def help(self, ctx, *input):
        """Shows all modules of the bot"""
        prefix = get_prefix(self.bot, ctx.message)
        if not input:
            # default help embed
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{prefix}help <module>` to gain more information about that module '
                                            f':smiley:\n')
            emb.add_field(name='Modules', value=self.cogs_desc, inline=False)
            if self.commands_desc:
                emb.add_field(name='Not belonging to a module',
                              value=self.commands_desc, inline=False)
            emb.add_field(
                name="About",
                value=f"Please visit https://github.com/Noob-Coders-Gang/Chintu-Bot to submit ideas or bugs.")
        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            # check if cog is the matching one
            if input[0].lower() in self.cogs:
                cog_name = self.cogs[input[0].lower()]
                # making title - getting description from doc-string below class
                emb = discord.Embed(title=f'{cog_name} - Commands', description=self.bot.cogs[cog_name].__doc__,
                                    color=discord.Color.green())

                # getting commands from cog
                for command in self.bot.get_cog(cog_name).get_commands():
                    # if cog is not hidden
                    if not command.hidden:
                        if command.help:
                            emb.add_field(
                                name=f"`{prefix}{command.name}`", value=command.help, inline=True)
                        else:
                            emb.add_field(
                                name=f"`{prefix}{command.name}`", value="ㅤ", inline=True)

            elif input[0].lower() in self.bot_commands:
                command = self.bot_commands[input[0].lower()]
                if not command.hidden:
                    emb = discord.Embed(title=f"${command.name} - Information", color=discord.Colour.green())
                    emb.add_field(name="Description:", value=command.help, inline=False)
                    if len(command.aliases) > 0:
                        emb.add_field(name="Aliases:", value=", ".join(command.aliases), inline=False)
                    emb.add_field(name="Usage:", value=f"${command.name} {command.signature}", inline=False)
                else:
                    emb = discord.Embed(title="What's that?!",
                                        description=f"I've never heard of a module or command called `{input[0]}` before :scream:",
                                        color=discord.Color.orange())

            # if input not found
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard of a module or command called `{input[0]}` before :scream:",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at once :sweat_smile:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="Oops Something went wrong.",
                                description='''Would you please be so kind to report that issue to me on github?\n"
                                            "https://github.com/Noob-Coders-Gang/Chintu-Bot\n''',
                                color=discord.Color.red())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)

    @commands.Cog.listener()
    async def on_update_prefix(self, ctx, prefix):
        update_guild_storage(guild_prefix_storage, ctx.guild.id, prefix)


def setup(bot):
    bot.add_cog(Help(bot))
