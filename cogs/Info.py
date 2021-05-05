import discord
import traceback
import random
import datetime

from discord import Member, Status
from discord.ext import commands


class Info(commands.Cog):
    """ Server , User Info and more"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, *,  avamember: discord.Member = None):
        ''' Get user avatar  '''
        userAvatarUrl = avamember.avatar_url
        embed = discord.Embed(title=f'{avamember} avatar!!', url=f"{userAvatarUrl}")
        embed.set_image(url=userAvatarUrl)
        await ctx.send(embed=embed)

    @commands.command(aliases=['channelstats'])
    async def channel_info(self, ctx, channel: discord.TextChannel):
        ''' get channel stats/info '''
        nsfw = self.bot.get_channel(channel.id).is_nsfw()
        news = self.bot.get_channel(channel.id).is_news()
        embed = discord.Embed(title='Channel Infromation: ' + str(channel),
                              colour=discord.Colour.from_rgb(54, 151, 255))
        embed.add_field(name='Channel Name: ', value=str(channel.name))
        embed.add_field(name="Channel's NSFW Status: ", value=str(nsfw))
        embed.add_field(name="Channel's id: ", value=str(channel.id))
        embed.add_field(name='Channel Created At: ', value=str(
            channel.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC")))
        embed.add_field(name='Channel Type: ', value=str(channel.type))
        embed.add_field(name="Channel's Announcement Status: ",
                        value=str(news))
        await ctx.send(embed=embed)

    @commands.command(aliases=['guild'])
    async def server(self, ctx):
        ''' Get Server Info '''
        findbots = sum(1 for member in ctx.guild.members if member.bot)
        embed = discord.Embed(title='Infomation about ' + ctx.guild.name +
                              '.', colour=discord.Colour.from_rgb(54, 151, 255))
        embed.set_thumbnail(url=str(ctx.guild.icon_url))
        embed.add_field(name="Guild's name: ", value=ctx.guild.name)
        embed.add_field(name="Guild's owner: ", value=str(ctx.guild.owner))
        embed.add_field(name="Guild's verification level: ",
                        value=str(ctx.guild.verification_level))
        embed.add_field(name="Guild's id: ", value=str(ctx.guild.id))
        embed.add_field(name="Guild's member count: ",
                        value=str(ctx.guild.member_count))
        embed.add_field(name="Bots", value=f"{findbots}", inline=True)
        embed.add_field(name="Guild created at: ", value=str(
            ctx.guild.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC")))
        await ctx.send(embed=embed)

    @commands.command(aliases=['whois', 'userinfo'])
    async def user(self, ctx, member: discord.Member = None):
        ''' Get User Info '''
        if member is None:
            member = ctx.author
        pos = sum(
            m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
        roles = [role for role in member.roles]
        embed = discord.Embed(color=discord.Colour.gold(),
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Joined at:", value=member.joined_at.strftime(
            "%a, %#d %B %Y, %I:%M %p"))
        embed.add_field(name='Registered at:', value=member.created_at.strftime(
            '%a, %#d %B %Y, %I:%M %p'))
        embed.add_field(name='Bot?', value=f'{member.bot}')

        if member.status == Status.online:
            status = "Online"
        elif member.status == (Status.do_not_disturb or Status.dnd):
            status = "DnD"
        else:
            status = "Offline"

        embed.add_field(name='Status?', value=f'{status}')
        embed.add_field(name='Top Role?', value=f'{member.top_role}')
        display_roles = ""
        for role in roles:
            display_roles += role.mention
        embed.add_field(name=f"Roles ({len(roles)})", value=f"{display_roles}")
        embed.add_field(name='Join position', value=f"{pos}")
        embed.set_footer(icon_url=member.avatar_url,
                         text=f'Requested By: {ctx.author.name}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
