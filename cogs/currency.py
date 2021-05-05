import asyncio
import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from main import database


class Currency(commands.Cog):
    """🤑 Everything related to da money 🤑"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.collection = database["currency"]
        self.defined_currencies = json.loads(
            open('./main_resources/Assets/currency_values.json', encoding='utf-8').read())
        self.items_by_id = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_id"]
        self.paged_shop, self.pages = create_paged_shop(self.items_by_id)

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
    async def balance(self, ctx: commands.Context, targeted_user: discord.Member = None):
        """Check the bank balance of those pesky scrubs"""
        if targeted_user is None:
            targeted_user = ctx.author
        coins = self.collection.find_one({"_id": targeted_user.id}, {"currency": 1})
        if coins is None:
            insert_new_document(self.collection, targeted_user.id)
            coins = {"currency": 0}
        if coins['currency'] == 0:
            emb = discord.Embed(description=f"***{targeted_user.display_name} currently has 0 coins. Poor much?***",
                                color=discord.Colour.green())
        else:
            emb = discord.Embed(
                description=f"***{targeted_user.display_name} currently has {coins['currency']} coins.***",
                color=discord.Colour.green())
        await ctx.send(embed=emb)

    @commands.command(aliases=['pay'])
    async def give(self, ctx: commands.Context, targeted_user: discord.Member, amount: int):
        """Give away your hard earned cash 🎁"""
        if ctx.author.id == targeted_user.id:
            await ctx.send(f"{ctx.author.mention}, you can't give coins to yourself. 😡")
            return
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, enter a value greater than 0. You can't fool me. 😡")
            return

        user_bal = self.collection.find_one(
            {"_id": ctx.author.id}, {"currency": 1})

        if user_bal is None:
            insert_new_document(self.collection, ctx.author.id)
            await ctx.send(f"{ctx.author.mention} You don't have enough coins lmao, get a job.")
            return
        elif user_bal["currency"] < amount:
            await ctx.send(f"{ctx.author.mention} You don't have enough coins lmao, get a job.")
            return
        else:
            self.collection.update_one({"_id": ctx.author.id}, {"$inc": {"currency": -amount}})
            self.collection.update_one({"_id": targeted_user.id},  # Query for update
                                       {
                                           "$inc": {"currency": amount},
                                           "$setOnInsert": {
                                               "inventory": {},
                                               "t_daily": 0,
                                               "t_weekly": 0,
                                               "t_monthly": 0
                                           }
                                       }, upsert=True)
            await ctx.send(
                f"** {ctx.author.mention} gave {amount} coins to {targeted_user.display_name}  <a:chintucoin:839401482184163358>**")

    @commands.command()
    async def shop(self, ctx: commands.Context, page_num: int = 1):
        """See what treasures await your purchase"""
        if self.pages >= page_num >= 1:
            embed = self.paged_shop[page_num - 1].set_footer(text=f"Page {page_num} of {self.pages}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid page number")

    @commands.command()
    async def buy(self, ctx: commands.Context, item: int, amount: int = 1):
        """Buy the items of your dreams from the shop <a:chintucoin:839401482184163358>"""
        if str(item) in self.items_by_id:
            if amount > 0:
                balance = self.collection.find_one({"_id": ctx.author.id}, {"currency": 1})
                if balance is not None:
                    balance = balance['currency']
                    item_dict = self.items_by_id[str(item)]
                    if balance >= self.items_by_id[str(item)]["value"] * amount:
                        embed = discord.Embed(
                            title=f"Do you want to purchase {amount} {item_dict['name']} for {item_dict['value'] * amount}?",
                            description="React with 👍 within 15 seconds to purchase", color=discord.Colour.green())
                        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        message = await ctx.send(embed=embed)
                        await message.add_reaction("👍")

                        def check(reaction, user):
                            return user.id == ctx.author.id and str(
                                reaction.emoji) == '👍' and reaction.message.id == message.id

                        try:
                            await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                            self.collection.update_one({"_id": ctx.author.id},
                                                       {"$inc": {
                                                           "currency": -item_dict["value"] * amount,
                                                           f"inventory.{str(item)}": amount
                                                       }})
                            await ctx.send(
                                f"{ctx.author.mention} You have successfully "
                                f"purchased {amount} {item_dict['name']} for {item_dict['value'] * amount}")
                        except asyncio.TimeoutError:
                            embed = discord.Embed(
                                title=f"Do you want to purchase {amount} {item_dict['name']} for {item_dict['value'] * amount}?",
                                description="Purchase failed. Please try again", color=discord.Colour.red())
                            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()
                    else:
                        await ctx.send(
                            f"{ctx.author.mention} You don't have enough money" +
                            f" for buying {self.items_by_id[str(item)]['name']}. Get a job lmao.")
                else:
                    insert_new_document(self.collection, ctx.author.id)
                    await ctx.send(
                        f"{ctx.author.mention} You don't have enough money" +
                        f" for buying {self.items_by_id[str(item)]['name']}. Get a job lmao.")
            else:
                await ctx.send(f"{ctx.author.mention} Enter a valid amount")

        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid item ID")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, targeted_user: discord.Member, amount: int):
        self.collection.update_one({"_id": targeted_user.id},  # Query for update
                                   {
                                       "$inc": {"currency": amount},
                                       "$setOnInsert": {
                                           "inventory": {},
                                           "t_daily": 0,
                                           "t_weekly": 0,
                                           "t_monthly": 0
                                       }
                                   }, upsert=True)
        emb = discord.Embed(description=f"***Added {amount} coins to {targeted_user.display_name}'s balance.***",
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


def create_paged_shop(items: dict):
    shop_items_len = len(items)
    pages = shop_items_len // 5
    if shop_items_len % 5 != 0:
        pages += 1

    embeds = []
    i = 0
    j = 0
    for item in items:
        if i == 0:
            embed = discord.Embed(title="Chintu Store")

        embed.add_field(name=f"{items[item]['name']} ─ {items[item]['value']}",
                        value=f"(ID - {item}) {items[item]['description']}", inline=False)
        i += 1
        j += 1
        if i == 4:
            embeds.append(embed)
            i = 0
        elif j == shop_items_len:
            embeds.append(embed)

    return embeds, pages


def setup(bot):
    bot.add_cog(Currency(bot))
