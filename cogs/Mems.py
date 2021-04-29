import praw
import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("SECRET"),
    user_agent='chintubot',
)


class redditapi():
    def memes(self, subreddit):
        memes = reddit.subreddit(subreddit)
        top = memes.top(limit=100)
        all_memes = []
        for meme in top:
            all_memes.append(meme)
        meme = random.choice(all_memes)
        meme_title = meme.title
        meme_url = meme.url
        return meme_title, meme_url


class Memes(commands.Cog):
    ''' Meme commads '''

    def __init__(self, commands):
        self.commands = commands

    @commands.command()
    async def csmeme(self, ctx):
        title, url = redditapi.memes('ProgrammerHumor')
        print(title, url)
        em = discord.Embed(title=title, color=discord.Colour.red())
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    async def meme(self, ctx):
        title, url = redditapi.memes('Memes')
        em = discord.Embed(title=title, color=discord.Colour.red())
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    async def foodporn(self, ctx):
        title, url = redditapi.memes('FoodPorn')
        em = discord.Embed(color=discord.Colour.red())
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    async def wsmeme(self, ctx):
        title, url = redditapi.memes('WholesomeMemes')
        em = discord.Embed(title=title, color=discord.Colour.red())
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    async def uwu(self, ctx):
        rand = random.randint(0, 2)
        if rand == 0:
            json = requests.get(
                "https://api.thecatapi.com/v1/images/search").json()
            url = str(json[0]["url"])
            title = "Here is a cat for you, uwu"
        elif rand == 1:
            json = requests.get(
                "https://dog.ceo/api/breeds/image/random").json()
            url = str(json["message"]).replace('\\', "/")
            title = "Here is a dog for you, owo"
        else:
            json = requests.get("https://randomfox.ca/floof/").json()
            url = str(json["image"]).replace('\\', "/")
            title = "Here is a fox for you, uwu"
        em = discord.Embed(title=title, color=discord.Colour.red())
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=str(
            ctx.author.avatar_url))
        await ctx.channel.send(embed=em)


def setup(bot):
    bot.add_cog(Memes(bot))
