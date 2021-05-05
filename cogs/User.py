import json

import discord
from discord.ext import commands
from main_resources.Item_use import *
from main import database


class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.items_by_id = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_id"]
        self.id_by_name = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_name"]
        self.bot = bot
        self.collection = database["currency"]

    @commands.command()
    async def use(self, ctx: commands.Context, item):
        item_dict = None
        try:
            item = int(item)
            if str(item) in self.items_by_id:
                item_dict = self.items_by_id[str(item)]
        except Exception:
            if item in self.id_by_name:
                item_dict = self.items_by_id[str(self.id_by_name[item])]
                item = self.id_by_name[item]
        if item_dict:
            inventory_dict = self.collection.find_one({"_id": ctx.author.id}, {"inventory": 1})["inventory"]
            if str(item) in inventory_dict and inventory_dict[str(item)] > 0:
                try:
                    if item_dict['type'] != "item":
                        await eval(item_dict['type'] + '(self.bot, ctx, item_dict)')
                    else:
                        await ctx.send("This item cannot be used.")
                except commands.MemberNotFound:
                    await ctx.send(f"Could't use {item_dict['name']}. Please report this issue using $suggest.")
            else:
                await ctx.send(
                    f"You do not have {item_dict['name']}. Buy it from the shop ($shop) before trying again.")
        else:
            await ctx.send(f"Could not find item with name or id {item}")


def setup(bot):
    bot.add_cog(User(bot))
