import discord
from discord.ext import commands
from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Images(commands.Cog):
    ''' Fun Images '''
    @commands.command()
    async def slap(self, ctx, user: discord.Member = None):

        user1 = ctx.author
        user2 = user
        if user == None:
            user2 = ctx.author

        slap = Image.open("main_resources/Images/slap.jpg")

        asset1 = user1.avatar_url_as(size=256)
        asset2 = user2.avatar_url_as(size=256)
        data1 = BytesIO(await asset1.read())
        data2 = BytesIO(await asset2.read())
        pfp1 = Image.open(data1)
        pfp1 = pfp1.resize((72, 72))
        slap.paste(pfp1, (131, 11))
        slap.save("main_resources/Images/send.jpg")
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((72, 72))
        slap.paste(pfp2, (11, 33))
        slap.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def worthless(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        worthless = Image.open("main_resources/Images/worthless.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((120, 120))
        worthless.paste(pfp, (148, 76))
        worthless.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command(aliases=['kq'])
    async def keepquiet(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        stop = Image.open("main_resources/Images/stop.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((220, 220))
        stop.paste(pfp, (695, 42))
        stop.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def fart(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        fart = Image.open("main_resources/Images/fart.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((200, 200))
        fart.paste(pfp, (532, 120))
        fart.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def pee(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        pee = Image.open("main_resources/Images/pee.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((210, 210))
        pee.paste(pfp, (432, 61))
        pee.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def coffindance(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        pee = Image.open("main_resources/Images/coffindance.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((127, 127))
        pee.paste(pfp, (196, 32))
        pee.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def smash(self, ctx, user: discord.Member = None):
        if user == None:
            user2 = ctx.author
        user1 = ctx.author
        user2 = user

        smash = Image.open("main_resources/Images/smash.jpg")

        asset1 = user1.avatar_url_as(size=256)
        asset2 = user2.avatar_url_as(size=256)
        data1 = BytesIO(await asset1.read())
        data2 = BytesIO(await asset2.read())
        pfp1 = Image.open(data1)
        pfp1 = pfp1.resize((91, 91))
        smash.paste(pfp1, (122, 167))
        smash.save("main_resources/Images/send.jpg")
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((88, 88))
        smash.paste(pfp2, (326, 290))
        smash.save("send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))

    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        wanted = Image.open("main_resources/Images/wantted.jpg")

        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((300, 300))
        wanted.paste(pfp, (81, 224))
        wanted.save("main_resources/Images/profile.jpg")
        await ctx.send(file=discord.File("main_resources/Images/profile.jpg"))

    @commands.command()
    async def gay(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author
        gay = Image.open("main_resources/Images/gay.jpg")

        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((199, 199))
        gay.paste(pfp, (32, 96))
        gay.save("main_resources/Images/send.jpg")
        await ctx.send(file=discord.File("main_resources/Images/send.jpg"))


def setup(bot):
    bot.add_cog(Images(bot))
