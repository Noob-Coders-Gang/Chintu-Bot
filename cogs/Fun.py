import discord
from discord.ext.commands.core import command
import requests
from discord.ext import commands
import random
import asyncio
import wikipedia
import urllib.request
import json
import math


class Fun(commands.Cog):
    """Fun commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball', 'test', 'ask'])
    async def _8ball(self, ctx, *, question):
        ''' Ask question and get advice from me '''
        responses = ["It is certain.",
                     "It is decidedly so.",
                     "Without a doubt.",
                     "Yes - definitely.",
                     "You may rely on it.",
                     "As I see it, yes.",
                     "Most likely.",
                     "Outlook good.",
                     "Yes.",
                     "Signs point to yes.",
                     "Reply hazy, try again.",
                     "Ask again later."
                     "Better not tell you now.",
                     "Cannot predict now.",
                     "Concentrate and ask again.",
                     "Don't count on it.",
                     "My reply is no.",
                     "My sources say no.",
                     "Outlook not so good.",
                     "Very doubtful."]
        em = discord.Embed(title='Magic 8ball!',
                           colour=discord.Colour.orange())
        em.add_field(name=f"**Question:** {question}",
                     value=f"**Answer:** {random.choice(responses)}")

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: str):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                with urllib.request.urlopen(f"https://v2.jokeapi.dev/joke/Any") as url:
                    url = json.loads(url.read().decode())
                print(url)
            except:
                pass

    @commands.command(aliases=["joke", "funjoke"])
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def jokes(self, ctx):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                with urllib.request.urlopen("https://v2.jokeapi.dev/joke/Any") as url:
                    url = json.loads(url.read().decode())

                def check(author):
                    def inner_check(message):
                        return message.author == author
                    return inner_check
                if(not url['error']):
                    if url["type"] == "twopart":
                        await ctx.send(url['setup'])
                        ans = await self.bot.wait_for('message', check=check, timeout=30)
                        if ans.content.lower().strip() == url['delivery'].lower().strip():
                            await ctx.send('Impresive , correct answer ')
                        else:
                            await ctx.send(url['delivery'])

                    else:
                        await ctx.send(url['joke'])

            except Exception as e:
                print(e)
                return await ctx.send("I am busy dude, I can't think any joke right now")

            if not url:
                return await ctx.send("I think the API broke...")

            if not len(url["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(url["list"], reverse=True,
                            key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."
            definition = definition.replace('[', "").replace("]", "")
            em = discord.Embed(
                title=f"📚 Definitions for **{result['word']}**", description=f"\n{definition}", color=discord.Colour.red())
            await ctx.send(embed=em)

    @commands.command()
    async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
        """ Give someone a beer! 🍻 """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.send(f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = beer_offer + \
            f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + \
                f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot"])
    async def hotcalc(self, ctx, *, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        if hot > 25:
            emoji = "❤"
        elif hot > 50:
            emoji = "💖"
        elif hot > 75:
            emoji = "💞"
        else:
            emoji = "💔"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command(aliases=['wikipedia'])
    async def wiki(self, ctx, *, querry_: str):
        ''' Search wikipedia for any information '''
        async with ctx.channel.typing():
            try:
                results = wikipedia.search(querry_, results=5)
                result_summary = wikipedia.summary(results[0])
                result_title = results[0]
                em = discord.Embed(title=result_title,
                                   color=discord.Color(0xf58742))
                em.set_footer(text=result_summary)
                em2 = discord.Embed(color=discord.Color(0xf58742))

                # em2.set_footer(text=f'Recommended searches : ' +
                #                f'{results[1:-1]}'[1:-1])
                await ctx.send(embed=em)
                # await ctx.send(embed=em2)
            except:
                await ctx.send("Sorry, I can find " + querry_ + " in Wikipedia")

    @commands.command()
    async def kill(self, ctx, user: discord.Member = None):
        ''' kill someone'''
        if user == None:
            user = ctx.author
        await ctx.send(f'{user.display_name} {random.choice(kills)}')

    @commands.command(aliases=['ppsize', 'size', 'penis'])
    async def pp(self, ctx, member: discord.Member):
        ''' To check pp size '''
        size = ['', '==', '', '=', '', '====', '', '=', '======', '==========================', '===', "===============",
                "========", "===", "===================", "===", '========', '=====', "======================================", "===", "============"]
        em = discord.Embed(color=discord.Colour.blue(),
                           title="PeePee size calculator")

        em.add_field(name=f"{member.display_name}s penis:eggplant:",
                     value=f"8{random.choice(size)}D")
        await ctx.send(embed=em)

    @commands.command(aliases=['how gay', 'gaypercent'])
    async def howgay(self, ctx, member: discord.Member):
        ''' To check gayness '''
        user = str(member.id)
        s = sum([int(x) for x in user])

        per = float((abs(math.sin((s/18)))) * 100)
        if per >= 50:
            gay = 'GAY'
        else:
            gay = "Not Gay"
        per = "{:.2f}".format(per)
        em = discord.Embed(title=member.display_name,
                           description=":two_men_holding_hands: gay result:", color=discord.Colour.red())
        em.add_field(
            name=gay, value=f"{member.display_name} is :rainbow_flag: {per}% gay ")
        em.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=em)

    @commands.command(aliases=['pass', 'generator', 'passwordgenerator'])
    async def password(self, ctx, amt: int = 8):
        ''' Generate random password  '''
        try:
            nwpss = []
            lst = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@',
                   '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', ",", '}', ']',
                   '[', ';', ':', '<', '>', '?', '/', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '`', '~', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            for x in range(amt):
                newpass = random.choice(lst)
                nwpss.append(newpass)
            fnpss = ''.join(nwpss)
            await ctx.send(f'{ctx.author} attempting to send you the genereated password in dms.')
            await ctx.author.send(f':white_check_mark:Password Generated: {fnpss}')
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Fun(bot))


#----------------------------------------------------------------#
kills = [
    "died from a creeper explosion",
    "died from lack of quality memes on Dank Memer",
    "disappeared from the universe.",
    "died from subscribing to t-series",
    "died from not subscribing to Pewdiepie",
    "ripped their own heart out to show their love for jhonny sins",
    "dies because they were just too angry😡 ",
    "chokes on cheerios and dies. What an idiot...",
    "died from patta se head shot 🔫",
    "was killed for being too noob.. what a noob",
    "died after fapping 50 times in a row with no break.",
    "because they were just too Lazy.",
    "was killed by imposter",
    "died from lack of ***, U got that 😁",
    "drowned in their own tears 😭.",
    "was eaten by the duolingo owl🦉 ",
    "dies, but don't let this distract you from the fact that in 1998, The Undertaker threw",
    "died from a nightmare👻 dream",
    "died while playing hopscotch on seemingly deactivated land mines.",
    "loses the will to live🤥",
    "died from whacking it too much. (There's a healthy balance, boys)",
    "eats too much copypasta and explodes",
    "reads memes till they die.",
    "dies of starvation.",
    "died somehow 🤷‍♂️",
    "died by taking sefi🤳 with lion🦁 ..such a idiot ",
    "died in 2020 for not wearing mask😷",
    "died from subscribing to t-series",
    "is dead. How 🤷🏼‍♂️",
    "died of scurvy, eat oranges kids",
    "cranks up the music system only to realize the volume was at max and the song playing was Baby by Justin Beiber..",
    "cranks up the music system only to realize the volume was at max and the song playing was selfie Maine le liya..",
    'died from watching to much of P**n 🤦‍♂️',
    'died from COVID-69, new virus transmitted from ga* s** 🚫🧑‍🤝‍🧑',
]
