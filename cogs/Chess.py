import os

import asyncio

import chess
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from cogs.utils.chess_utils import ChessUtils
import berserk

"""
{'type': 'gameState', 
'moves': 'g1f3', 
'wtime': datetime.datetime(1970, 1, 25, 20, 31, 23, 647000, tzinfo=datetime.timezone.utc), 
'btime': datetime.datetime(1970, 1, 25, 20, 31, 23, 647000, tzinfo=datetime.timezone.utc), 
'winc': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 
'binc': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 
'wdraw': False, 
'bdraw': False, 
'status': 'started'}

"""


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        session = berserk.TokenSession(os.getenv("ACCESS_TOKEN"))
        self.client = berserk.Client(session)
        self.utils = ChessUtils(self.client)

    @commands.group(invoke_without_command=True, name="chess")
    async def chess(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please enter a subcommand")

    @chess.command(name="import")
    async def _import(self, ctx: Context, lichess_game_id: str):
        """Show a game from Lichess.org"""
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
                    if position_index < len(positions) - 1:
                        position_index += 1
                        if position_index == len(positions) - 1:
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

    @chess.command(name="play")
    async def play(self, ctx: Context, level: int, color: str = "white"):
        dump_channel = self.bot.get_channel(int(os.getenv("DUMP_CHANNEL", "868392499348144180")))
        WHITE = berserk.Color.WHITE
        BLACK = berserk.Color.BLACK
        level, color, headers, board = setup_game(ctx, level, color)
        game_dict = self.utils.create_ai_game(level, color)
        game_id = game_dict["id"]
        message = await send_attachment_embed(ctx, dump_channel, **self.utils.render_board(board, headers))
        looper = Loop_creator(self.bot, self.client, game_id)
        looper.start_gameState_listener.start()

        def check(game_id_check, last_move_check, len_moves):
            return game_id_check == game_dict["id"]

        def check_user_move(msg):
            return msg.author.id == ctx.author.id and len(msg.content) == 4

        if color == WHITE:
            await ask_user_for_move(ctx, self.client, self.bot, check_user_move, board, game_id)

        while True:
            await edit_attachment_embed(message, dump_channel, **self.utils.render_board(board, headers))
            game_id, last_move, len_moves = await self.bot.wait_for('move', check=check)
            if len_moves % 2 == 0:
                if color == WHITE:
                    await ask_user_for_move(ctx, self.client, self.bot, check_user_move, board, game_id)
                else:
                    continue
            else:
                if color == WHITE:
                    continue
                else:
                    await ask_user_for_move(ctx, self.client, self.bot, check_user_move, board, game_id)


class Loop_creator:
    def __init__(self, bot, client, game_id):
        self.game_id = game_id
        self.client = client
        self.bot = bot

    @tasks.loop(count=1)
    async def start_gameState_listener(self):
        stream = self.client.bots.stream_game_state(self.game_id)
        for event in stream:
            if event['type'] == 'gameState':
                last_move = event['moves'].split()[-1]
                len_moves = len(event['moves'].split())
                self.bot.dispatch("move", self.game_id, last_move, len_moves)


async def send_attachment_embed(ctx: Context, dump_channel: discord.TextChannel, embed, file):
    dump_message = await dump_channel.send(file=file)
    message = await ctx.send(embed=embed.set_image(url=dump_message.attachments[0].url))
    return message


async def edit_attachment_embed(message: discord.Message, dump_channel: discord.TextChannel, embed, file):
    dump_message = await dump_channel.send(file=file)
    message = await message.edit(embed=embed.set_image(url=dump_message.attachments[0].url))
    return message


async def ask_user_for_move(ctx, client, bot, check, board, game_id):
    legal = False
    while not legal:
        await ctx.send(f"{ctx.author.mention} Make a move, You have 30 seconds to make a move")
        message = await bot.wait_for("message", check=check, timeout=30.0)
        content = message.content.lower()
        try:
            client.bots.make_move(game_id, content)
            board.push(content)
            legal = True
        except:
            await ctx.send(f"{ctx.author.mention} Please make a legal move")


def setup_game(ctx, level: int, color: str):
    if level < 0:
        level = 0
    elif level > 8:
        level = 8
    if color.lower() == "black":
        color = berserk.Color.BLACK
        headers = {
            "White": "Stockfish",
            "Black": ctx.author.name,
            "WhiteElo": f"Level {level}",
            "BlackElo": "Unkown",
            "Event": "Unrated Versus AI",
            "Result": "Unkown"
        }
    else:
        color = berserk.Color.WHITE
        headers = {
            "White": ctx.author.name,
            "Black": "Stockfish",
            "WhiteElo": "Unkown",
            "BlackElo": f"Level {level}",
            "Event": "Unrated Versus AI",
            "Result": "Unkown"
        }
    board = chess.Board()
    return level, color, headers, board


def setup(bot):
    bot.add_cog(Chess(bot))
