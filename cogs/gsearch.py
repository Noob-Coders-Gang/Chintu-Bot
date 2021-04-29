from urllib import parse
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


class Google(commands.Cog):
    '''Commands to search google  '''

    def __init__(self, commands):
        self.commands = commands

    @commands.command(aliases=['google', 'search'])
    async def gsearch(self, ctx: discord.ext.commands.Context, *, query):
        """Sends top google search result with page description"""
        searchInput = "https://google.com/search?q=" + \
            parse.quote(query) + "&num=2"  # Query url for top 2 results
        res = requests.get(searchInput)  # Gets the google search results page
        # Parses the google search results page
        soup = BeautifulSoup(res.text, "html.parser")
        tag = list(soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).parent.parent.parent.parent.find('div', {
            'class': 'BNeawe s3v9rd AP7Wnd'}).find_all('div', {'class': 'BNeawe s3v9rd AP7Wnd'}))  # Creates a list of parsable search results
        # Gets the description for the parsable search result
        text = ""
        for div in tag:
            if div.find(text=True, recursive=False) != " " and div.find(text=True, recursive=False) is not None:
                text = div.find(text=True, recursive=False)
                break
        # Creates an embed with the relevant data, ie Result title, its url and its description
        embed = discord.Embed(title=soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).get_text(),
                              url=soup.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).parent.parent.get(
                                  "href").split('=')[1],
                              description=text)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Google(bot))
