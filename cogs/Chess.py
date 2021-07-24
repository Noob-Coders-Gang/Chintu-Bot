import os

import asyncio
from discord.ext import commands
from discord.ext.commands import Context
from cogs.utils.chess_utils import ChessUtils
import berserk


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        session = berserk.TokenSession(os.getenv("ACCESS_TOKEN"))
        client = berserk.Client(session)
        self.utils = ChessUtils(client)

    @commands.group(invoke_without_command=True, name="chess")
    async def chess(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please enter a subcommand")

    @chess.command(name="import")
    async def _import(self, ctx: Context, lichess_game_id: str):
        dump_channel = self.bot.get_channel(int(os.getenv("DUMP_CHANNEL", "868392499348144180")))
        game = self.utils.import_game_by_id(lichess_game_id)
        positions = list(game.mainline())
        position_index = 0
        embed, image_file = self.utils.create_position_embed(game, game.board())
        dump_message = await dump_channel.send(file=image_file)
        message = await ctx.send(embed=embed.set_image(url=dump_message.attachments[0].url))
        await message.add_reaction("◀")
        await message.add_reaction("▶")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == message.id and (str(
                reaction.emoji) == "◀" or str(
                reaction.emoji) == "▶")

        try:
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶":
                    if position_index < len(positions)-1:
                        position_index += 1
                        if position_index == len(positions)-1:
                            embed, image_file = self.utils.create_position_embed(game,
                                                                                 positions[position_index].board(),
                                                                                 end=True)
                        else:
                            embed, image_file = self.utils.create_position_embed(game,
                                                                                 positions[position_index].board())
                        dump_message = await dump_channel.send(file=image_file)
                        await message.edit(embed=embed.set_image(url=dump_message.attachments[0].url))
                elif str(reaction.emoji) == "◀":
                    if position_index > 0:
                        position_index -= 1
                        embed, image_file = self.utils.create_position_embed(game, positions[position_index].board())
                        dump_message = await dump_channel.send(file=image_file)
                        await message.edit(embed=embed.set_image(url=dump_message.attachments[0].url))
                await reaction.remove(user)
        except asyncio.TimeoutError:
            return


def setup(bot):
    bot.add_cog(Chess(bot))
