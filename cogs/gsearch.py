from urllib import parse
import discord
from discord.ext import commands
from googlesearch import search
import requests
from bs4 import BeautifulSoup


class Google(commands.Cog):
    def __init__(self, commands):
        self.commands = commands

    @commands.command(aliases=['google', 'search'])
    async def gsearch(self, ctx: discord.ext.commands.Context, *, query):
        """Sends top google search result with page description"""
        searchInput = "https://google.com/search?q=" + parse.quote(query) + "&num=2"
        res = requests.get(searchInput)
        soup = BeautifulSoup(res.text, "html.parser")
        tag = list(soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).parent.parent.parent.parent.find('div', {
            'class': 'BNeawe s3v9rd AP7Wnd'}).find_all('div', {'class': 'BNeawe s3v9rd AP7Wnd'}))
        text = ""
        for div in tag:
            if div.find(text=True, recursive=False) != " " and div.find(text=True, recursive=False) is not None:
                text = div.find(text=True, recursive=False)
                break
        embed = discord.Embed(title=soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).get_text(),
                              url=soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).parent.parent.get("href").split('=')[1],
                              description=text)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Google(bot))