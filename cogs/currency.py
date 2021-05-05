import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from main import database


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
        daily_time = self.collection.find_one({"_id": ctx.author.id}, {"t_daily": 1})

        if daily_time is None \
                or daily_time['t_daily'] == 0 \
                or (datetime.utcnow() - daily_time['t_daily']) >= timedelta(days=1):
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                                           "$inc": {"currency": self.defined_currencies['daily']},
                                           "$set": {"t_daily": datetime.utcnow()},
                                           "$setOnInsert": {
                                               "inventory": {},
                                               "t_weekly": 0,
                                               "t_monthly": 0
                                           }
                                       }, upsert=True)
            emb = discord.Embed(title="Enjoy your daily cold hard cash 🤑",
                                description=f"{self.defined_currencies['daily']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your daily again in:", value="24 hours")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your daily coins", color=discord.Colour.green())
            del_time = (daily_time['t_daily'] + timedelta(days=1)) - datetime.utcnow()
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
            member = ctx.author
        coins = self.collection.find_one({"_id": member.id}, {"currency": 1})
        if coins is None:
            insert_new_document(self.collection, member.id)
            coins = {"currency": 0}
        if coins['currency'] == 0:
            emb = discord.Embed(description=f"***{member.name} currently has 0 coins. Poor much?***",
                                color=discord.Colour.green())
        else:
            emb = discord.Embed(description=f"***{member.name} currently has {coins['currency']} coins.***",
                                color=discord.Colour.green())
        await ctx.send(embed=emb)

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
        emb = discord.Embed(description=f"***Added {amount} coins to {member.name}'s balance.***",
                            color=discord.Colour.green())
        await ctx.send(embed=emb)


def insert_new_document(collection, doc_id: int, currency: int = 0, inventory=None, t_daily: datetime = 0,
                        t_weekly: datetime = 0,
                        t_monthly: datetime = 0):
    if inventory is None:
        inventory = {}
    collection.insert_one({
        "_id": doc_id,
        "currency": currency,
        "inventory": inventory,
        "t_daily": t_daily,
        "t_weekly": t_weekly,
        "t_monthly": t_monthly
    })


def setup(bot):
    bot.add_cog(Currency(bot))
