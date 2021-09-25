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

        game = GameGrid.GameGrid(str(ctx.author.id), str(ctx.author.name), str(ctx.author.avatar_url))
        game.start()

        message = await ctx.send(game.getEmojiMessage())

        game.setMessageId(str(message.id))
        game.setChannelId(str(ctx.channel.id))

        await message.add_reaction('⬆')
        await message.add_reaction('⬇')
        await message.add_reaction('➡')
        await message.add_reaction('⬅')
        await message.add_reaction('❌')

    @commands.command(aliases=['rps'])
    async def rockpaperscissors(self, ctx):
    ch1 = ["Rock","Scissors","Paper"]
    comp = choice(ch1)
    
    yet = discord.Embed(title = f"{ctx.author.display_name}'s Rock Paper Scissors Game!", description = f"Status: You haven't clicked on any button yet!", color =  ctx.author.color)
    
    win = discord.Embed(title = f"{ctx.author.display_name}, You Won!", description = f"Status: **You have won!** Bot chose {comp}", color =  0x00FF00)
    
    out = discord.Embed(title = f"{ctx.author.display_name},  You did not click on time!", description = f"Status: **Timed Out!**", color =  discord.Colour.red())
    
    lost = discord.Embed(title = f"{ctx.author.display_name}, You Lost!!", description = f"Status: **You have Lost!** Bot had chosen {comp}", color =  discord.Color.red())
  
    tie = discord.Embed(title = f"{ctx.author.display_name}, It was a Tie!", description = f"Status: **Tie!**, Bot had chosen {comp}", color =  ctx.author.color)
    m = await ctx.send(
        embed=yet,
        components=[[Button(style=1, label="Rock"),Button(style=3, label="Paper"),Button(style=ButtonStyle.red, label="Scissors")]
        ],
    )

    def check(res):
        return ctx.author == res.user and res.channel == ctx.channel

    try:
        res = await client.wait_for("button_click", check=check, timeout=15)
        player = res.component.label
        
        if player==comp:
          await m.edit(embed=tie,components=[])
          
        if player=="Rock" and comp=="Paper":
          await m.edit(embed=lost,components=[])
          
        if player=="Rock" and comp=="Scissors":
          await m.edit(embed=win,components=[])
        
        
        if player=="Paper" and comp=="Rock":
          await m.edit(embed=win,components=[])
          
        if player=="Paper" and comp=="Scissors":
          await m.edit(embed=lost,components=[])
          
          
        if player=="Scissors" and comp=="Rock":
          await m.edit(embed=lost,components=[])
          
        if player=="Scissors" and comp=="Paper":
          await m.edit(embed=win,components=[])
        

    except TimeoutError:
        await m.edit(
          embed=out,
          components=[],
            )       
def setup(bot):
    bot.add_cog(Minigames(bot))
