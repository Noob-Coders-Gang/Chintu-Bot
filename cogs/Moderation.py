import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import find
import main


class BannedUser(commands.Converter):
    async def convert(self, ctx, arg):
        banned = [e.user for e in await ctx.guild.bans()]
        if banned:
            user = find(lambda u: str(u) == arg, banned)
            if user:
                return user
            else:
                raise commands.BadArgument



class Moderation(commands.Cog):
    ''' Moderator Commands '''

    def __init__(self, commands: commands.Bot):
        self.commands = commands
        self.warn_collection = main.database["warns"]

    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def warn(self, ctx: commands.Context, warned_member: discord.Member, *, reason: str = None):
        if reason is None:
            reason = "No reason was provided"
        warn_id = random.randint(10000000, 99999999)
        check_repeat_dict = self.warn_collection.find_one({"_id": warn_id})
        while check_repeat_dict:
            warn_id = random.randint(10000000, 9999999)
            check_repeat_dict = self.warn_collection.find_one({"_id": warn_id})
        warn_dict = {
            "_id": warn_id,
            "guild_id": ctx.guild.id,
            "member_id": warned_member.id,
            "member_name": warned_member.name,
            "reason": reason,
            "message_id": ctx.message.id,
            "moderator_id": ctx.author.id,
            "moderator_name": ctx.author.name,
            "channel_id": ctx.channel.id,
            "time": datetime.utcnow().timetuple()
        }
        self.warn_collection.insert_one(warn_dict)
        try:
            user_embed = discord.Embed(title=f"You have been warned in {ctx.guild.name}",
                                       description=f"Reason: {reason}", color=discord.Colour.orange())
            await warned_member.send(embed=user_embed)
            channel_embed = discord.Embed(title=f"{warned_member.name} has been warned",
                                          description=f"Reason: {reason}", color=discord.Colour.orange())
            channel_embed.set_footer(text=f"Warned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=channel_embed)
        except Exception:
            channel_embed = discord.Embed(
                title=f"Warning for {warned_member.name} has been logged. I couldn't DM them.",
                description=f"Reason: {reason}", color=discord.Colour.orange())
            channel_embed.set_footer(text=f"Warned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=channel_embed)

    @commands.command(name="warns")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def warns(self, ctx: commands.Context, member: discord.Member):
        warns = list(self.warn_collection.find(
            {"member_id": member.id, "guild_id": ctx.guild.id}))
        embed = discord.Embed(
            title=f"{member.name} has been warned {len(warns)} times", color=discord.Colour.orange())
        for warn in warns:
            embed.add_field(
                name=f"Warn ID: {warn['_id']}",
                value=f"Reason: {str(warn['reason'])}, Warned by: {warn['moderator_name']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="warninfo")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def warninfo(self, ctx: commands.Context, warn_id: int):
        warn = self.warn_collection.find_one({'_id': warn_id})
        if warn is not None:
            if ctx.guild.id == warn['guild_id']:
                embed = discord.Embed(
                    title=f"Warn information for warn ID:{warn_id}", color=discord.Colour.orange())
                embed.add_field(name="Warned member",
                                value=warn['member_name'], inline=False)
                embed.add_field(name="Warned by",
                                value=warn['moderator_name'], inline=False)
                embed.add_field(
                    name="Warn link",
                    value=f"[Message Link](https://discord.com/channels/{warn['guild_id']}/{warn['channel_id']}/{warn['message_id']})",
                    inline=False)
                embed.add_field(name="Reason", value=warn['reason'], inline=False)
                timetuple = warn['time']
                embed.add_field(
                    name="Warned at",
                    value=f"{timetuple[2]}/{timetuple[1]}/{timetuple[0]} {timetuple[3]}:{timetuple[4]} (UTC)",
                    inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{ctx.author.mention} Warn not found!")
        else:
            await ctx.send(f"{ctx.author.mention} Warn not found!")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member, *, reason):
        """Kicks the mentioned member"""
        embed = discord.Embed(
            description=str(
                str(member) + " is Kicked | reason = " + reason),
            colour=discord.Colour.green()
        )
        await member.send(embed=embed)
        await member.kick(reason=reason)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans the mentioned member"""
        if not reason:
            reason = "No reason was provided"
        embed = discord.Embed(
            description=str(member) + " has been banned | reason = " + reason,
            colour=discord.Colour.green()
        )
        try:
            await member.send(embed=embed)
        except Exception:
            pass
        finally:
            await member.ban(reason=reason)

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mutedRole:
            bot_integration_role = ctx.guild.me.roles[-1]
            mutedRole = await ctx.guild.create_role(name="Muted", color=0x000000)
            await mutedRole.edit(position=bot_integration_role.position-1)
            for channel in ctx.guild.channels:
                await channel.set_permissions(mutedRole, send_messages=False)
        if not reason:
            reason = "No reason was provided."
        embed = discord.Embed(title=str(str(member) + " has been Muted | reason = " + reason),
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)
        await member.add_roles(mutedRole, reason=reason)
        try:
            await member.send(f" you have been muted in {ctx.guild.name} | Reason: {reason}")
        except Exception:
            return

    @commands.command(name="unmute")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def unmute(self, ctx, member: discord.Member, *, reason="No reason specified"):
        """Unmutes the mentioned member"""
        Muted = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(Muted)
        embed = discord.Embed(
            description=str(
                str(member) + " has been Unmuted | reason = " + reason),
            colour=discord.Colour.green()
        )
        await member.send(embed=embed)

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def clear(self, ctx, number_of_messages: int = 5):
        """Purges specified number of messages"""
        await ctx.channel.purge(limit=number_of_messages + 1)
        embed = discord.Embed(title=f"Deleted {number_of_messages} in {ctx.channel.name}")
        emb_msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await emb_msg.delete()


def setup(bot):
    bot.add_cog(Moderation(bot))
