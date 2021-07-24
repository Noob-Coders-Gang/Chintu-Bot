import io

import cairosvg
import chess
import chess.pgn
import chess.svg
import discord
from abc import ABC
"""
sus={'id': 'WXyKWw1q', 
     'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 
     'speed': 'correspondence', 
     'perf': 'correspondence', 
     'rated': False, 
     'initialFen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 
     'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 
     'player': 'white', 
     'turns': 0, 
     'startedAtTurn': 0, 
     'source': 'ai', 
     'status': {'id': 20, 'name': 'started'}, 
     'createdAt': 1627135755014
}
"""


class ChessUtils:
    def __init__(self, client):
        self.client = client

    def import_game_by_id(self, game_id: str):
        pgn = str(self.client.games.export(game_id, as_pgn=True))
        game = chess.pgn.read_game(io.StringIO(pgn))
        return game

    def import_last_game_by_player(self, player_name: str):
        pgn = list(self.client.games.export_by_player(player_name, max=1, as_pgn=True))[0]
        game = chess.pgn.read_game(io.StringIO(pgn))
        return game

    def save_moves_as_png(self, game: chess.pgn.GameNode):
        ply = 1
        for position in game.mainline():
            self.save_position_as_png(position.board(), ply)
            ply += 1

    def create_ai_game(self, level:int, color):
        if level < 0:
            level = 0
        elif level > 8:
            level = 8
        return self.client.challenges.create_ai(level=level, color=color)

    @classmethod
    def save_position_as_png(cls, board: chess.Board, ply: int):
        boardsvg = chess.svg.board(board=board)
        cairosvg.svg2png(file_obj=io.StringIO(str(boardsvg)), write_to=f"move{ply}.png")

    @classmethod
    def create_position_embed(cls, game: chess.pgn.Game, board: chess.Board, end=False):
        board_svg = chess.svg.board(board)
        png_bytes = cairosvg.svg2png(file_obj=io.StringIO(str(board_svg)))
        file = discord.File(io.BytesIO(png_bytes), filename="chess.png")
        embed = discord.Embed(
            title=f":white_circle: {game.headers['White']}({game.headers['WhiteElo']}) vs. "
                  f":black_circle: {game.headers['Black']}({game.headers['BlackElo']})",
            description=f"Event: {game.headers['Event']} | Result: {game.headers['Result']}{' | End of game' if end else ''}"
        )
        return embed, file

    @classmethod
    def render_board(cls, board:chess.Board, headers):
        board_svg = chess.svg.board(board)
        png_bytes = cairosvg.svg2png(file_obj=io.StringIO(str(board_svg)))
        file = discord.File(io.BytesIO(png_bytes), filename="chess.png")
        embed = discord.Embed(
            title=f":white_circle: {headers['White']}({headers['WhiteElo']}) vs. "
                  f":black_circle: {headers['Black']}({headers['BlackElo']})",
            description=f"Event: {headers['Event']} | Result: {headers['Result']}"
        )
        return embed, file
