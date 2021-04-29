import json
import discord
from discord.ext import commands
import pickle
import logging
from cogs.data_classes.warning import Warn
import main
import traceback
from datetime import datetime
import random


class Mod(commands.Cog):
    ''' Moderator Commands '''

    def __init__(self, commands):
        self.commands = commands
        self.warn_collection = main.database["warns"]

    
    @commands.command()
    async def warn(self, ctx:commands.Context, warned_member:discord.Member, reason:str=None): 
        ctx.send("Under development")
        


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
    async def clear(self, ctx, number_of_messages=5):
        """Purges specified number of messages"""
        print("deleting")
        await ctx.channel.purge(limit=number_of_messages + 1)


def setup(bot):
    bot.add_cog(Mod(bot))

    # @commands.command()
    # @commands.has_permissions(kick_members=True)
    # async def warn(self, ctx, member: discord.Member, *, reason='No reason Provided'):
    #     """Warns a member with the provided reason"""
    #     # with open('warnings.json', 'r') as f:
    #     #     warns = json.load(f)
    #     # if str(ctx.guild.id) not in warns:
    #     #     warns[str(ctx.guild.id)] = {}
    #     # if str(member.id) not in warns[str(ctx.guild.id)]:
    #     #     warns[str(ctx.guild.id)][str(member.id)] = {}
    #     #     warns[str(ctx.guild.id)][str(member.id)]["warns"] = 1
    #     #     warns[str(ctx.guild.id)][str(member.id)]["warnings"] = [reason]
    #     # else:
    #     #     warns[str(ctx.guild.id)][str(member.id)]["warnings"].append(reason)
    #     # with open('warnings.json', 'w') as f:
    #     #     json.dump(warns, f)
    #     #     # await ctx.send(f"{member.mention} was warned for: {reason}")

    #     embed1 = discord.Embed(title='You have been warned ', description=f'You received a warning from {member}')
    #     embed = discord.Embed(title=f'{member.mention} has been warned', description=f"Description - {reason}")
    #     embed.add_field(name='Reason:', value=f'{reason}')
    #     await ctx.send(embed = embed)
    #     embed = discord.Embed(title=f'{member} has been warned', description=f"Description - {reason}")
    #     embed1.add_field(name='Reason:', value=f'{reason}')
    #     await ctx.send(embed=embed)
    #     await member.send(embed=embed1)
    #     # print(reason)
    #     # embed = discord.Embed(
    #     #    description=str(member + " is warned | Reason = " + reason),
    #     #    colour=discord.Colour.blue()
    #     # )
    #     # await send_messeage_to_general(self ,ctx, embed)

    # @commands.command()
    # async def warns(self, ctx, member: discord.Member):
    #     """Gives warnings received by the mentioned member"""
    #     with open('warnings.json', 'r') as f:
    #         warns = json.load(f)
    #     num = 1
    #     warnings = discord.Embed(title=f'{member}\'s warns ')
    #     for warn in warns[str(ctx.guild.id)][str(member.id)]["warnings"]:
    #         warnings.add_field(name=f"Warn {num}", value=warn)
    #         num += 1
    #     await ctx.send(embed=warnings)

    # @commands.command()
    # @commands.has_permissions(kick_members=True)
    # async def removewarn(self, ctx, member: discord.Member, num: int, *, reason='No reason provided.'):
    #     """Removes specified warn from warnings.json"""
    #     with open('warnings.json', 'r') as f:
    #         warns = json.load(f)
    #     num -= 1
    #     warns[str(ctx.guild.id)][str(member.id)]["warns"] -= 1
    #     warns[str(ctx.guild.id)][str(member.id)]["warnings"].pop(num)
    #     with open('warnings.json', 'w') as f:
    #         json.dump(warns, f)
    #         await ctx.send('Warn has been removed!')
    #         embed = discord.Embed(title='Your warn has been removed',
    #                               description=f'Your warning was removed by {ctx.author}')
    #         await member.send(embed=embed)
    # @commands.command()
    # @commands.has_permissions(ban_members=True)
    # async def role(self, ctx, member: discord.Member):
    #     """asks tagged user to take roles"""
    #     embed = discord.Embed(
    #         description=str(
    #             str(
    #                 member) + " please take roles from #♦-roles, age and gender roles are mandatory, misleading roles will be rewarded with a ban! "),
    #         colour=discord.Colour.green()
    #     )
    #     await member.send(embed=embed)
# """Collection setup:
#         [
#             {
#                 "_id":<discord user id>,
#                 "guilds":{
#                     <guild id>:{
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         }
#                     },
#                     <guild id>:{
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         }
#                     }
#                 }
#             },
#             {
#                 "_id":<discord user id>,
#                 "guilds":{
#                     <guild id>:{
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         }
#                     },
#                     <guild id>:{
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         },
#                         <warn_id>:{
#                             "warn_reason":<reason>,
#                             "date-time":<datetime>
#                         }
#                     }
#                 }
#             }
#         ]
#         """
# if reason is None:
#             reason = "No reason was provided"
#         warn_id = random.randint(10000000, 99999999)
#         warn_obj = Warn(warn_id, ctx.author.id, ctx.message.id, reason, datetime.now())
#         pickled_string = pickle.dumps(warn_obj)
#         document = {
#             "_id":warn_id,
#             "member_id":warned_member.id,
#             "guild_id":ctx.guild.id,
#             "message_id":ctx.message.id,
#             "warn_object":pickled_string
#         }
#         self.warn_collection.insert_one(document)
#         channel_embed = discord.Embed(title=f"{warned_member.mention} has been warned", description=f"Reason: {reason}")
#         channel_embed.set_footer(text=f"Warned by {ctx.author.id}", image=ctx.author.avatar_url)
#         await ctx.send(channel_embed)