import discord
import requests
from discord.ext import commands
from discord.ext.commands import CommandError


class GitHub(commands.Cog):
    '''  Search Github Profile '''

    def __init__(self, commands):
        self.commands = commands

    def __srt__(self):
        return ''' Search Github Profile '''

    @commands.command(name="repos", aliases=["repositories", "github"])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def repos(self, ctx: discord.ext.commands.Context, username):
        """Sends top 5 repositories of the requested user"""
        user_data = requests.get(
            f"https://api.github.com/users/{username}").json()
        if "message" in user_data:
            em = discord.Embed(title=f"User {username} not found! Please check the username.",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            raise CommandError
        repos_data = requests.get(
            f"https://api.github.com/users/{username}/repos").json()
        embed = discord.Embed(
            title=f"Top 5 repositories of {username}", color=discord.Color.blue())
        embed.set_thumbnail(url=user_data)
        embed.set_footer(
            text=f"{username} has {user_data['public_repos']} repositories!")
        if len(repos_data) > 5:
            repos_data = repos_data[:5]
        for result in repos_data:
            embed.add_field(name=result["name"],
                            value=result["html_url"], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="gituser", aliases=["gitmember"])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def gituser(self, ctx, username):
        """Sends info about a github user"""
        user_data = requests.get(
            f"https://api.github.com/users/{username}").json()
        if "message" in user_data:
            em = discord.Embed(title=f"User {username} not found! Please check the username.",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            raise CommandError
        embed = discord.Embed(title=username, color=discord.Color.blue())
        embed.set_thumbnail(url=user_data["avatar_url"])
        embed.add_field(name="URL", value=user_data["html_url"])
        attributes = {"name": "Name", "company": "Company", "blog": "Website", "location": "Location",
                      "bio": "Github Bio", "twitter_username": "Twitter Handle", "public_repos": "Total Repos"}
        for attribute in attributes:
            if user_data[attribute] is not None:
                if user_data[attribute] != "":
                    embed.add_field(
                        name=attributes[attribute], value=user_data[attribute], inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GitHub(bot))
