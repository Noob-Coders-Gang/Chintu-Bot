import asyncio
import random
import traceback
from datetime import datetime

import discord
import youtube_dl
from discord.ext import commands

from cogs.currency_utils.utils import currency_utils
from main import database

collection = database["currency"]
utils = currency_utils(collection)

properties = {}
for doc in collection.find({}, {"properties": 1, "_id": 1}):
    if "properties" in doc:
        properties[doc["_id"]] = doc["properties"]


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
    if ctx.author.id in properties:
        if "100_uses" in properties[ctx.author.id]:
            properties[ctx.author.id]["100_uses"] += uses
            utils.update(ctx.author.id, inc_vals={"properties.100_uses": uses})
        else:
            properties[ctx.author.id]["100_uses"] = uses
            utils.update(ctx.author.id, inc_vals={"properties.100_uses": uses})
    else:
        properties[ctx.author.id] = {"100_uses": uses}
        utils.update(ctx.author.id, inc_vals={"properties.100_uses": uses})
    await ctx.send(
        f"{ctx.author.mention} You used Joe Mama. {uses} uses were added and a total of {properties[ctx.author.id]['100_uses']} uses are left.")


# async def ring(bot, ctx:commands.Context, item_dict: dict):
#     converter = commands.MemberConverter
#     message_list = ctx.message.content.replace(ctx.prefix, "").split(" ")
#     if len(message_list) < 1
#     mentioned_user = await converter.convert(ctx, )


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


def properties_100(ctx: commands.Context):
    if ctx.author.id not in properties or "100_uses" not in properties[ctx.author.id] or \
            properties[ctx.author.id]["100_uses"] <= 0:
        return f"{ctx.author.mention} You have 0 Joe Mama replies."
    else:
        return f'{ctx.author.mention} You have {properties[ctx.author.id]["100_uses"]} Joe Mama replies.'


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
