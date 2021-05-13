import discord
from discord.ext import commands
from dotenv import load_dotenv

import main

load_dotenv()


class manage_commands(commands.Cog):
    ''' add or remove commands in a server'''

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.cmd_list = []
        for cmd in bot.commands:
            # Get all commands registered with the bot
            self.cmd_list.append(cmd.name)

    @commands.command()
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def remove(self, ctx: commands.Context, command_name: str):
        ''' Remove commands '''
        if command_name in self.cmd_list:
            # Get the cmd_manager collection from the database
            collection = main.database["cmd_manager"]
            try:
                current_guild = collection.find_one({"_id": ctx.guild.id})
                # Get currently disabled command list
                current_list = current_guild["disabled_commands"]
                if command_name not in current_list:
                    # Add the requested command to the disabled command list
                    current_list.append(command_name)
                collection.update_one({"_id": ctx.guild.id}, {
                    "$set": {"disabled_commands": current_list}})  # Update the collection
                embed = discord.Embed(title=f"I have removed the {command_name} command from your server!",
                                      color=discord.Colour.green())
                await ctx.send(embed=embed)
            except Exception:
                embed = discord.Embed(title=f"An error occurred!",
                                      color=discord.Colour.green())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def add(self, ctx: commands.Context, command_name: str):
        ''' Add commands'''
        if command_name in self.cmd_list:
            # Get the cmd_manager collection from the database
            collection = main.database["cmd_manager"]
            try:
                current_guild = collection.find_one({"_id": ctx.guild.id})
                # Get currently disabled command list
                current_list = current_guild["disabled_commands"]
                if command_name in current_list:
                    # Remove the requested command from the disabled command list
                    current_list.remove(command_name)
                collection.update_one({"_id": ctx.guild.id}, {
                    "$set": {"disabled_commands": current_list}})  # Update the collection
                embed = discord.Embed(title=f"I have added the {command_name} command back to your server!",
                                      color=discord.Colour.green())
                await ctx.send(embed=embed)
            except Exception:
                embed = discord.Embed(title=f"An error occurred!",
                                      color=discord.Colour.green())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(manage_commands(bot))
