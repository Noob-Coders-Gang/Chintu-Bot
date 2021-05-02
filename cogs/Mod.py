import discord
from discord.ext import commands
import main
from datetime import datetime
import random



class Mod(commands.Cog):
    ''' Moderator Commands '''

    def __init__(self, commands: commands.Bot):
        self.commands = commands
        self.warn_collection = main.database["warns"]
        self.warn_collection.insert_one


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx:commands.Context, warned_member:discord.Member, *, reason:str=None):
        if reason is None:
            reason = "No reason was provided"
        warn_id = random.randint(10000000, 99999999)
        check_repeat_dict = self.warn_collection.find_one({"_id":warn_id})
        while check_repeat_dict:
            warn_id = random.randint(10000000, 9999999)
            check_repeat_dict = self.warn_collection.find_one({"_id":warn_id})
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
            user_embed = discord.Embed(title=f"You have been warned in {ctx.guild.name}", description=f"Reason: {reason}")
            await warned_member.send(embed=user_embed)
            channel_embed = discord.Embed(title=f"{warned_member.name} has been warned", description=f"Reason: {reason}")
            channel_embed.set_footer(text=f"Warned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=channel_embed)
        except Exception:
            channel_embed = discord.Embed(title=f"Warning for {warned_member.name} has been logged. I couldn't DM them.", 
                                          description=f"Reason: {reason}")
            channel_embed.set_footer(text=f"Warned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=channel_embed)
            
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx: commands.Context, member: discord.Member):
        warns = list(self.warn_collection.find(
            {"member_id": member.id, "guild_id": ctx.guild.id}))
        embed = discord.Embed(
            title=f"{member.name} has been warned {len(warns)} times")
        for warn in warns:
            embed.add_field(
                name=f"Warn ID: {warn['_id']}", value=f"Reason: {str(warn['reason'])}, Warned by: {warn['moderator_name']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warninfo(self, ctx: commands.Context, warn_id: int):
        warn = self.warn_collection.find_one({'_id': warn_id})
        if ctx.guild.id == warn['guild_id']:
            embed = discord.Embed(
                title=f"Warn information for warn ID:{warn_id}")
            embed.add_field(name="Warned member",
                            value=warn['member_name'], inline=False)
            embed.add_field(name="Warned by",
                            value=warn['moderator_name'], inline=False)
            embed.add_field(
                name="Warn link", value=f"https://discord.com/channels/{warn['guild_id']}/{warn['channel_id']}/{warn['message_id']}", inline=False)
            embed.add_field(name="Reason", value=warn['reason'], inline=False)
            timetuple = warn['time']
            embed.add_field(
                name="Warned at", value=f"{timetuple[2]}/{timetuple[1]}/{timetuple[0]} {timetuple[3]}:{timetuple[4]} (UTC)", inline=False)
            await ctx.send(embed=embed)
        else:
            ctx.send("Warn not found!")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason):
        """Kicks the mentioned member"""
        print(reason)
        embed = discord.Embed(
            description=str(
                str(member) + " is Kicked | reason = " + reason),
            colour=discord.Colour.green()
        )
        await member.send(embed=embed)
        await member.kick(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason):
        """Bans the mentioned member"""
        print(reason)
        embed = discord.Embed(
            description=str(
                str(member) + " is banned | reason = " + reason),
            colour=discord.Colour.green()
        )
        await member.send(embed=embed)
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason):
        """Gives muted role to the mentioned user"""
        print(reason)
        Muted = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(Muted)
        embed = discord.Embed(
            description=str(
                str(member) + " is Muted | reason = " + reason),
            colour=discord.Colour.red()
        )
        await member.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="No reason specified"):
        """Unmutes the mentioned member"""
        print(reason)
        Muted = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(Muted)
        embed = discord.Embed(
            description=str(
                str(member) + " is Unmuted | reason = " + reason),
            colour=discord.Colour.green()
        )
        await member.send(embed=embed)

    @commands.command(aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number_of_messages:int=5):
        """Purges specified number of messages"""
        print("deleting")
        await ctx.channel.purge(limit=number_of_messages + 1)


def setup(bot):
    bot.add_cog(Mod(bot))

 
