import asyncio
import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from main import database
import numpy as np


class Currency(commands.Cog):
    """🤑 Everything related to da money 🤑"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.collection = database["currency"]
        self.defined_currencies = json.loads(
            open('./main_resources/Assets/currency_values.json', encoding='utf-8').read())
        self.items_by_id = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_id"]
        self.id_by_name = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_name"]
        self.paged_shop, self.pages = create_paged_shop(self.items_by_id)
        self.houses = {
            1: "5 of a kind",
            2: "4 of a kind",
            3: "3 of a kind and a pair",
            4: "2 pairs",
            5: "1 pair",
            6: "None of the accepted combinations"
        }
        self.prizes = {
            5: 2,
            4: 1.5,
            3: 1.3,
            2: 1.2,
            1: 1
        }

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
            emb = discord.Embed(title="You have already claimed your daily coins", color=discord.Colour.red())
            del_time = (daily_time['t_daily'] + timedelta(days=1)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            emb.add_field(name="You can claim your daily again in:",
                          value=f"{hours} hours, {minutes} minutes and {seconds} seconds")
            await ctx.send(embed=emb)

    @commands.command()
    async def weekly(self, ctx: commands.Context):
        """Weekly dose of sweet cash 💰💰💰"""
        weekly_time = self.collection.find_one({"_id": ctx.author.id}, {"t_weekly": 1})

        if weekly_time is None \
                or weekly_time['t_weekly'] == 0 \
                or (datetime.utcnow() - weekly_time['t_weekly']) >= timedelta(days=7):
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                                           "$inc": {"currency": self.defined_currencies['weekly']},
                                           "$set": {"t_weekly": datetime.utcnow()},
                                           "$setOnInsert": {
                                               "inventory": {},
                                               "t_daily": 0,
                                               "t_monthly": 0
                                           }
                                       }, upsert=True)
            emb = discord.Embed(title="Enjoy your weekly cold hard cash 🤑",
                                description=f"{self.defined_currencies['weekly']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your weekly again in:", value="7 days")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your weekly coins", color=discord.Colour.red())
            del_time = (weekly_time['t_weekly'] + timedelta(days=7)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = (days * 24 + seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            # seconds = seconds % 60
            emb.add_field(name="You can claim your weekly again in:",
                          value=f"{days} days, {hours} hours and {minutes} minutes")
            await ctx.send(embed=emb)

    @commands.command()
    async def monthly(self, ctx: commands.Context):
        """Monthly dose of sweet cash 💰💰💰"""
        monthly_time = self.collection.find_one({"_id": ctx.author.id}, {"t_monthly": 1})

        if monthly_time is None \
                or monthly_time['t_monthly'] == 0 \
                or (datetime.utcnow() - monthly_time['t_monthly']) >= timedelta(days=30):
            self.collection.update_one({"_id": ctx.author.id},  # Query for update
                                       {
                                           "$inc": {"currency": self.defined_currencies['monthly']},
                                           "$set": {"t_monthly": datetime.utcnow()},
                                           "$setOnInsert": {
                                               "inventory": {},
                                               "t_daily": 0,
                                               "t_weekly": 0
                                           }
                                       }, upsert=True)
            emb = discord.Embed(title="Enjoy your monthly cold hard cash 🤑",
                                description=f"{self.defined_currencies['monthly']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your monthly again in:", value="30 days")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your monthly coins", color=discord.Colour.red())
            del_time = (monthly_time['t_monthly'] + timedelta(days=30)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = (days * 24 + seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            # seconds = seconds % 60
            emb.add_field(name="You can claim your monthly again in:",
                          value=f"{days} days, {hours} hours and {minutes} minutes")
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
    async def shop(self, ctx: commands.Context, page: int = 1):
        """See what treasures await your purchase"""
        if self.pages >= page >= 1:
            embed = self.paged_shop[page - 1].set_footer(text=f"Page {page} of {self.pages}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid page number")

    @commands.command()
    async def gift(self, ctx: commands.Context, target_user: discord.Member, item: str, amount: int = 1):
        """Give away your precious items 🎁"""
        item_dict = None
        item_id = None
        item = item.lower()
        if item in self.items_by_id:
            item_dict = self.items_by_id[item]
            item_id = item
        elif item in self.id_by_name:
            item_dict = self.items_by_id[str(self.id_by_name[item])]
            item_id = str(self.id_by_name[item])

        if item_dict is not None and item_id is not None:
            if amount > 0:
                inventory = self.collection.find_one({"_id": ctx.author.id}, {"inventory": 1})
                if inventory is not None:
                    inventory = inventory["inventory"]
                    if item_id in inventory and inventory[item_id] >= amount:
                        embed = discord.Embed(
                            title=f"Do you want to gift {amount} {item_dict['name']} to {target_user.name}?",
                            description="React with 👍 within 15 seconds to confirm", color=discord.Colour.green())
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
                                                           f"inventory.{item_id}": -amount
                                                       }})
                            self.collection.update_one({"_id": target_user.id},
                                                       {
                                                           "$inc": {f"inventory.{item_id}": amount},
                                                           "$setOnInsert": {
                                                               "currency": 0,
                                                               "t_daily": 0,
                                                               "t_weekly": 0,
                                                               "t_monthly": 0
                                                           }
                                                       }, upsert=True)
                            await ctx.send(
                                f"{ctx.author.mention} You have successfully "
                                f"gifted {amount} {item_dict['name']} to {target_user.name}")
                        except asyncio.TimeoutError:
                            embed = discord.Embed(
                                title=f"Do you want to gift {amount} {item_dict['name']} to {target_user.name}?",
                                description="Gift failed. Please try again", color=discord.Colour.red())
                            embed.set_footer(text=f"Requested by {ctx.author.display_name}",
                                             icon_url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()
                    else:
                        await ctx.send(f"{ctx.author.mention} Lmao you don't have {amount} {item_dict['name']} to"
                                       f" gift.")
                else:
                    insert_new_document(self.collection, ctx.author.id)
                    await ctx.send(f"{ctx.author.mention} Lmao you don't have {amount} {item_dict['name']} to gift.")
            else:
                await ctx.send(f"{ctx.author.mention} Enter a valid amount")
        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid item ID or name")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item, amount: int = 1):
        """Buy the items of your dreams from the shop <a:chintucoin:839401482184163358>"""
        item_dict = None
        item = item.lower()
        try:
            item = int(item)
            if str(item) in self.items_by_id:
                item_dict = self.items_by_id[str(item)]
        except Exception:
            if item in self.id_by_name:
                item_dict = self.items_by_id[str(self.id_by_name[item])]
                item = self.id_by_name[item]
        if item_dict is not None:
            if amount > 0:
                balance = self.collection.find_one({"_id": ctx.author.id}, {"currency": 1})
                if balance is not None:
                    balance = balance['currency']
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
                            embed.set_footer(text=f"Requested by {ctx.author.display_name}",
                                             icon_url=ctx.author.avatar_url)
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
            await ctx.send(f"{ctx.author.mention} Enter a valid item ID or name")

    @commands.command()
    async def bet(self, ctx: commands.Context, amount: str):
        """Join in on some gambling action, similar to Klondike dice game"""
        try:
            amount = int(amount)
        except:
            if amount.lower() == "max" or amount.lower() == "all":
                balance = self.collection.find_one({"_id": ctx.author.id}, {"currency": 1})
                if balance is None:
                    try:
                        insert_new_document(self.collection, ctx.author.id)
                    except:
                        pass
                    await ctx.send(f"{ctx.author.mention} Lmao you don't have enough coins to bet.")
                    return
                if balance['currency'] >= 250000:
                    amount = 250000
                else:
                    amount = balance['currency']
            else:
                await ctx.send(f"{ctx.author.mention} Enter a proper amount or max/all.")

        if 250000 >= amount >= 50:
            balance = self.collection.find_one({"_id": ctx.author.id}, {"currency": 1})
            if balance is not None and balance['currency'] >= amount:
                bot_pair, user_pair = find_pairs(np.random.randint(1, 6, 5)), find_pairs(np.random.randint(1, 6, 5))
                if bot_pair <= user_pair:
                    embed = discord.Embed(title=f"{ctx.author.display_name}'s losing bet",
                                          description=f"You lost {amount} coins",
                                          color=discord.Colour.red())
                    embed.add_field(name="Chintu rolled:", value=self.houses[bot_pair])
                    embed.add_field(name="You rolled:", value=self.houses[user_pair])
                    self.collection.update_one({"_id": ctx.author.id}, {"$inc": {"currency": -amount}})
                else:
                    embed = discord.Embed(title=f"{ctx.author.display_name}'s winning bet",
                                          description=f"You won {int(amount*self.prizes[bot_pair-user_pair]+amount)} coins",
                                          color=discord.Colour.green())
                    embed.add_field(name="Chintu rolled:", value=self.houses[bot_pair])
                    embed.add_field(name="You rolled:", value=self.houses[user_pair])
                    self.collection.update_one({"_id": ctx.author.id}, {"$inc": {"currency": int(amount*self.prizes[bot_pair-user_pair])}})
                await ctx.send(embed=embed)
            else:
                try:
                    insert_new_document(self.collection, ctx.author.id)
                except:
                    pass
                await ctx.send(f"{ctx.author.mention} Lmao you don't have enough coins to bet.")
        elif amount >= 250000:
            await ctx.send(f"{ctx.author.mention} If I let you bet more than 50,000 coins, you'd be broke in no time.")
        else:
            await ctx.send(f"{ctx.author.mention} Enter an amount greater than 50 coins")

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


def find_pairs(array: np.ndarray):
    len_without_dup = len(set(array))
    arr_set = list(set(array))
    arr_sum = np.sum(array)
    if len_without_dup > 3:
        return len_without_dup + 1
    elif len_without_dup == 1:
        return len_without_dup
    elif len_without_dup == 3:
        set_sum = np.sum(arr_set)
        if arr_sum - arr_set[0] * 3 == set_sum - arr_set[0] or arr_sum - arr_set[1] * 3 == set_sum - arr_set[
            1] or arr_sum - arr_set[0] * 3 == set_sum - arr_set[0]:
            return 6
        else:
            return 4
    if arr_set[0] * 4 + arr_set[1] == arr_sum or arr_set[1] * 4 + arr_set[0] == arr_sum:
        return 2
    else:
        return 3


def setup(bot):
    bot.add_cog(Currency(bot))
