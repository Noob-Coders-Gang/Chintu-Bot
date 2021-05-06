import json
from datetime import datetime

from main import database
from main_resources.Item_use import *


class User(commands.Cog):
    """All of your personal data I stole."""

    def __init__(self, bot: commands.Bot):
        self.items_by_id = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_id"]
        self.id_by_name = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_name"]
        self.bot = bot
        self.collection = database["currency"]

    @commands.command()
    async def use(self, ctx: commands.Context, item):
        """Use the items you got there in your inventory"""
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

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx: commands.Context, target_user=None, page_number=1):
        """Check what you have in your inventory"""
        if target_user is None:
            target_user = ctx.author
            page_number = 1
        else:
            try:
                converter = commands.MemberConverter()
                target_user = await converter.convert(ctx, target_user)
                page_number = page_number
            except Exception:
                try:
                    page_number = int(target_user)
                    target_user = ctx.author
                except Exception:
                    await ctx.send("Enter valid page number")
        inventory_dict = self.collection.find_one({"_id": target_user.id}, {"inventory": 1})
        if inventory_dict is not None:
            inventory_dict = inventory_dict['inventory']
            total_items = len(inventory_dict)
            pages = int((total_items - 1) // 5 + 1 + (total_items - 1) % 5 / 10)
            if pages != 0:
                if 0 < page_number <= pages:
                    keys = list(inventory_dict.keys())
                    embed = discord.Embed(title=f"{target_user.name}'s Inventory")
                    if page_number == pages:
                        limit = total_items
                    else:
                        limit = page_number * 5
                    for i in range((page_number - 1) * 5, limit):
                        item_id_str = keys[i]
                        embed.add_field(
                            name=f"{self.items_by_id[item_id_str]['emoji']} {self.items_by_id[item_id_str]['name']} ─ {inventory_dict[item_id_str]}",
                            value=f"(ID - {item_id_str}) {self.items_by_id[item_id_str]['description']}", inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Enter a valid page number")
            else:
                await ctx.send("The inventory is empty lmao. To buy something use $shop")
        else:
            insert_new_document(self.collection, target_user.id)
            await ctx.send("The inventory is empty lmao. To buy something use $shop")


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
    bot.add_cog(User(bot))
