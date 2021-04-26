import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import main
load_dotenv()


class manage_commands(commands.Cog):
    def __init__(self, bot:discord.ext.commands.Bot):
        self.bot = bot
        self.cmd_list = []
        for cmd in bot.commands:
            self.cmd_list.append(cmd.name) # Get all commands registered with the bot
        


    @commands.command()
    async def remove(self, ctx:commands.Context, command_name:str):
        if command_name in self.cmd_list:
            collection = main.database["cmd_manager"] # Get the cmd_manager collection from the database
            try:
                current_guild = collection.find_one({"_id":ctx.guild.id}) 
                current_list = current_guild["disabled_commands"] # Get currently disabled command list
                if command_name not in current_list:
                    current_list.append(command_name) # Add the requested command to the disabled command list
                collection.update_one({"_id":ctx.guild.id},{"$set":{"disabled_commands":current_list}}) # Update the collection
                embed = discord.Embed(title=f"I have removed the {command_name} command from your server!",
                                        color=discord.Colour.green())
                await ctx.send(embed=embed)
            except Exception:
                embed = discord.Embed(title=f"An error occurred!",
                                        color=discord.Colour.green())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)
    

    @commands.command()
    async def add(self, ctx:commands.Context, command_name:str):
        if command_name in self.cmd_list:
            collection = main.database["cmd_manager"] # Get the cmd_manager collection from the database
            try:
                current_guild = collection.find_one({"_id":ctx.guild.id})
                current_list = current_guild["disabled_commands"] # Get currently disabled command list
                if command_name in current_list:
                    current_list.remove(command_name) # Remove the requested command from the disabled command list
                collection.update_one({"_id":ctx.guild.id},{"$set":{"disabled_commands":current_list}}) # Update the collection
                embed = discord.Embed(title=f"I have added the {command_name} command back to your server!",
                                        color=discord.Colour.green())
                await ctx.send(embed=embed)
            except Exception:
                embed = discord.Embed(title=f"An error occurred!",
                                        color=discord.Colour.green())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"I don't have any command named {command_name}", color=discord.Colour.red())
            await ctx.send(embed=embed)
                

def setup(bot):
    bot.add_cog(manage_commands(bot))
