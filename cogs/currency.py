import discord
from discord.ext import commands
from main import database
import json
import traceback
from datetime import datetime, timedelta


class Currency(commands.Cog):
    """🤑 Everything related to da money 🤑"""

    def __init__(self, bot):
        self.bot = bot
        self.collection = database["currency"]
        self.defined_currencies = json.loads(
            open('./main_resources/Assets/currency_values.json', encoding='utf-8').read())

    @commands.command()
    async def daily(self, ctx: commands.Context):
        """Daily dose of sweet cash 💰💰💰"""
        # if self.collection.count_documents({"_id":ctx.author.id}) > 0:
        daily_time = self.collection.find_one(
            {"_id": ctx.author.id}, {"t_daily": 1})

        if daily_time is None:
            self.collection.insert_one({
                "_id": ctx.author.id,
                "currency": self.defined_currencies['daily'],
                "inventory": {},
                "t_daily": datetime.utcnow(),
                "t_weekly": 0,
                "t_monthly": 0
            })
            emb = discord.Embed(title="Enjoy your daily cold hard cash 🤑",
                                description=f"{self.defined_currencies['daily']} coins were placed in your wallet!", color=discord.Colour.green())
            emb.add_field(
                name="You can claim your daily again in:", value="24 hours")
            await ctx.send(embed=emb)

        elif daily_time['t_daily'] == 0:
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                # Increase value of currency by defined value
                "$inc": {"currency": self.defined_currencies['daily']},
                # Set daily time
                "$set": {"t_daily": datetime.utcnow()},
            })
            emb = discord.Embed(title="Enjoy your daily cold hard cash 🤑",
                                description=f"{self.defined_currencies['daily']} coins were placed in your wallet!", color=discord.Colour.green())
            emb.add_field(
                name="You can claim your daily again in:", value="24 hours")
            await ctx.send(embed=emb)

        elif (datetime.utcnow() - daily_time['t_daily']) >= timedelta(days=1):
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                # Increase value of currency by defined value
                "$inc": {"currency": self.defined_currencies['daily']},
                # Set daily time
                "$set": {"t_daily": datetime.utcnow()},
            })
            emb = discord.Embed(title="Enjoy your daily cold hard cash 🤑",
                                description=f"{self.defined_currencies['daily']} coins were placed in your wallet!", color=discord.Colour.green())
            emb.add_field(
                name="You can claim your daily again in:", value="24 hours")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(
                title="You have already claimed your daily coins", color=discord.Colour.green())
            del_time = (daily_time['t_daily'] +
                        timedelta(days=1))-datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            emb.add_field(name="You can claim your daily again in:",
                          value=f"{hours} hours, {minutes} minutes and {seconds} seconds")
            await ctx.send(embed=emb)

    @commands.command(aliases=['bal'])
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        """Check the bank balance of those pesky scrubs"""
        if member is None:
            coins = self.collection.find_one(
                {"_id": ctx.author.id}, {"currency": 1})
            if coins is None:
                self.collection.insert_one({
                    "_id": ctx.author.id,
                    "currency": 0,
                    "inventory": {},
                    "t_daily": 0,
                    "t_weekly": 0,
                    "t_monthly": 0
                })
                emb = discord.Embed(
                    description=f"***{ctx.author.name} currently has 0 coins. Poor much?***", color=discord.Colour.green())
            else:
                emb = discord.Embed(
                    description=f"***{ctx.author.name} currently has {coins['currency']} coins <a:chintucoin:839401482184163358>.***", color=discord.Colour.green())
        else:
            coins = self.collection.find_one(
                {"_id": member.id}, {"currency": 1})
            if coins is None:
                self.collection.insert_one({
                    "_id": member.id,
                    "currency": 0,
                    "inventory": {},
                    "t_daily": 0,
                    "t_weekly": 0,
                    "t_monthly": 0
                })
                emb = discord.Embed(
                    description=f"***{member.name} currently has 0 coins. Poor much?***", color=discord.Colour.green())
            else:
                emb = discord.Embed(
                    description=f"***{member.name} currently has {coins['currency']} coins.***", color=discord.Colour.green())
        await ctx.send(embed=emb)

    @commands.command()
    async def give(self, ctx, targeted_user: discord.Member, amount: int):
        """ giveaway part of your coins 🎁 """
        if ctx.author == targeted_user:
            await ctx.send(f"{ctx.author.name} you cant give coin to yourself")
            return 0

        userbal = self.collection.find_one(
            {"_id": ctx.author.id}, {"currency": 1})
        if userbal is None:
            self.collection.insert_one({
                "_id": ctx.author.id,
                "currency": 0,
                "inventory": {},
                "t_daily": 0,
                "t_weekly": 0,
                "t_monthly": 0
            })
        if userbal["currency"] < amount:
            await ctx.send("You don't have enough coin, poor af")
            return 0

        if amount > 0:
            target = self.collection.find_one(
                {"_id": targeted_user.id}, {"currency": 1})

            if target is None:
                self.collection.insert_one({
                    "_id": targeted_user.id,
                    "currency": 0,
                    "inventory": {},
                    "t_daily": 0,
                    "t_weekly": 0,
                    "t_monthly": 0
                })
            self.collection.update_one({"_id": targeted_user.id},  # Query for update
                                       {
                # Increase value of currency by defined value
                "$inc": {"currency": amount}
            })
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                # Increase value of currency by defined value
                "$inc": {"currency": -amount}
            })
            await ctx.send(f"** {ctx.author.name} gave {amount} coins to {targeted_user.display_name}  <a:chintucoin:839401482184163358>**")
        else:
            await ctx.send("***Enter in a value greater than 0***")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, member: discord.Member, amount: int):
        self.collection.update_one({"_id": member.id},  # Query for update
                                   {
            "$inc": {"currency": amount},
            "$setOnInsert": {
                "inventory": {},
                "t_daily": 0,
                "t_weekly": 0,
                "t_monthly": 0
            }
        }, upsert=True)
        emb = discord.Embed(
            description=f"***Added {amount} coins to {member.name}'s balance.***", color=discord.Colour.green())
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Currency(bot))
