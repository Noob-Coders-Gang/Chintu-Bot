import asyncio
import random
import traceback
from datetime import datetime

import discord
import youtube_dl
from discord.ext import commands
from discord.ext.commands import CommandError

from cogs.currency_utils.utils import currency_utils
from main import database

collection = database["currency"]
utils = currency_utils(collection)

properties = {}
for doc in collection.find({}, {"properties": 1, "_id": 1}):
    if "properties" in doc:
        properties[doc["_id"]] = doc["properties"]


def update_properties():
    properties.clear()
    for document in collection.find({}, {"properties": 1, "_id": 1}):
        if "properties" in document:
            properties[document["_id"]] = document["properties"]


def update_user_properties(id_: int):
    document = collection.find_one({"_id": id_}, {"properties": 1, "_id": 1})
    properties[id_] = document["properties"]


async def disc(bot, ctx: commands.Context, item_dict: dict):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send(f"{ctx.author.mention} You must be in a voice channel to use this item.")
        return
    if ctx.voice_client is None:
        client = await channel.connect()
    else:
        client = ctx.voice_client
        if client.channel != channel:
            await client.move_to(channel)
    try:
        msg = await ctx.send("Playing your disc now.")
        url = item_dict['url']
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        if client.is_playing():
            client.stop()
        client.play(player)
        await msg.add_reaction("✅")
        while client.is_playing():
            await asyncio.sleep(1)
        await client.disconnect()
    except:
        if client:
            await client.disconnect()
        traceback.print_exc()


async def notebook(bot, ctx: commands.Context, item_dict: dict):
    await ctx.send("Under Development")


async def mom(bot, ctx: commands.Context, item_dict: dict):
    uses = random.randint(10, 50)
    utils.update(ctx.author.id, inc_vals={"properties.100_uses": uses})
    update_user_properties(ctx.author.id)
    await ctx.send(
        f"{ctx.author.mention} You used Joe Mama. {uses} uses were added and a total of {properties[ctx.author.id]['100_uses']} uses are left.")


async def ring(bot, ctx: commands.Context, item_dict: dict):
    converter = commands.MemberConverter()
    message_list = ctx.message.content.replace(ctx.prefix, "").split(" ")
    if len(message_list) != 3:
        await ctx.send(f"{ctx.author.mention} Mention a user to marry them!")
        raise CommandError
    try:
        mentioned_user = await converter.convert(ctx, message_list[2])
    except:
        await ctx.send(f"{ctx.author.mention} Couldn't find user {message_list[2]}")
        raise CommandError
    if ctx.author.id in properties and f"{item_dict['id']}_member" in properties[ctx.author.id] and \
            properties[ctx.author.id][f"{item_dict['id']}_member"] is not None:
        await ctx.send(
            f"{ctx.author.mention} You are already married! Buy and use Divorce papers from the shop to marry someone else")
        raise CommandError
    if mentioned_user.id in properties and f"{item_dict['id']}_member" in properties[mentioned_user.id] and \
            properties[mentioned_user.id][f"{item_dict['id']}_member"] is not None:
        await ctx.send(
            f"{ctx.author.mention}, {mentioned_user.display_name} is already married to someone else! Ask them to divorce their significant other using Divorce papers from the shop")
        raise CommandError
    embed = discord.Embed(
        title=f"{mentioned_user.display_name}, {ctx.author.display_name} has proposed you with a {item_dict['name']} "
              f"ring! Would you like to marry them?",
        description="React with 👍 within 15 seconds to confirm", color=discord.Colour.green())
    embed.set_footer(text=f"Pls marry this loner", icon_url=ctx.author.avatar_url)
    message = await ctx.send(mentioned_user.mention, embed=embed)
    await message.add_reaction("👍")

    def check(reaction, user):
        return user.id == mentioned_user.id and str(
            reaction.emoji) == '👍' and reaction.message.id == message.id

    try:
        await bot.wait_for('reaction_add', timeout=15.0, check=check)
        time_of_marriage = datetime.utcnow()
        utils.update(ctx.author.id,
                     set_vals={f"properties.{item_dict['id']}_member.id": mentioned_user.id,
                               f"properties.{item_dict['id']}_member.name": mentioned_user.display_name,
                               f"properties.{item_dict['id']}_member.datetime": time_of_marriage},
                     inc_vals={f"inventory.{item_dict['id']}": -1})
        utils.update(mentioned_user.id,
                     set_vals={f"properties.{item_dict['id']}_member.id": ctx.author.id,
                               f"properties.{item_dict['id']}_member.name": ctx.author.display_name,
                               f"properties.{item_dict['id']}_member.datetime": time_of_marriage})
        utils.update(ctx.author.id)
        await ctx.send(
            f"{ctx.author.mention} and {mentioned_user.mention} are now married to each other! Please don't ask them to invite you on their honeymoon")
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title=f"{mentioned_user.display_name}, {ctx.author.display_name} has proposed you with a {item_dict['name']} "
                  f"ring! Would you like to marry them?",
            description=f"Proposal failed. I guess {mentioned_user.display_name} doesn't like you",
            color=discord.Colour.red())
        await message.edit(embed=embed)
        await message.clear_reactions()
        raise CommandError


def properties_100(ctx: commands.Context):
    if ctx.author.id not in properties or "100_uses" not in properties[ctx.author.id] or \
            properties[ctx.author.id]["100_uses"] <= 0:
        return f"{ctx.author.mention} You have 0 Joe Mama replies."
    else:
        return f'{ctx.author.mention} You have {properties[ctx.author.id]["100_uses"]} Joe Mama replies.'


def properties_104(ctx: commands.Context):
    if ctx.author.id not in properties or "104_member" not in properties[ctx.author.id]:
        return f"{ctx.author.mention} You are not married to any user."
    else:
        del_time = datetime.utcnow() - properties[ctx.author.id]['104_member']['datetime']
        days, seconds = del_time.days, del_time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{ctx.author.mention} You are married to {properties[ctx.author.id]['104_member']['name']} since {days} " \
               f"days, {hours} hours and {minutes} minutes"


async def on_message(bot: commands.Bot, message: discord.Message):
    if len(message.mentions) > 0:
        mentioned_member: discord.User = message.mentions[0]
    else:
        return
    if mentioned_member.id not in properties or "100_uses" not in properties[mentioned_member.id] or \
            properties[mentioned_member.id][
                "100_uses"] <= 0 or mentioned_member.id == message.author.id or message.author.id == bot.user.id:
        return
    if "ur" in message.content.lower() or "you're" in message.content.lower() or "youre" in message.content.lower():
        try:
            webhook: discord.Webhook = await message.channel.create_webhook(name=mentioned_member.name)
            await webhook.send(f"{message.author.mention} no ur mom", username=mentioned_member.name,
                               avatar_url=mentioned_member.avatar_url)
            await webhook.delete()
        except commands.MissingPermissions:
            await message.channel.send(f"{message.author.mention} no ur mom")
        finally:
            properties[mentioned_member.id]["100_uses"] -= 1
            utils.update(mentioned_member.id, inc_vals={"properties.100_uses": -1})


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
