from discord.ext import commands
from cogs.utils import GameGrid

class Minigames(commands.Cog):
    """Minigames"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="2048")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def _2048(self, ctx):
        """Play 2048"""

        if GameGrid.getGamesByUser(str(ctx.author.id)) is not None:
            game = GameGrid.getGamesByUser(str(ctx.author.id))
            message = await ctx.send(game.getEmojiMessage())

            game.setMessageId(str(message.id))
            game.setChannelId(str(ctx.channel.id))

            await message.add_reaction('⬆')
            await message.add_reaction('⬇')
            await message.add_reaction('➡')
            await message.add_reaction('⬅')
            await message.add_reaction('❌')
            return

        game = GameGrid.GameGrid(f'{ctx.author.id}')
        game.start()

        message = await ctx.send(game.getEmojiMessage())

        game.setMessageId(str(message.id))
        game.setChannelId(str(ctx.channel.id))

        await message.add_reaction('⬆')
        await message.add_reaction('⬇')
        await message.add_reaction('➡')
        await message.add_reaction('⬅')
        await message.add_reaction('❌')

def setup(bot):
    bot.add_cog(Minigames(bot))