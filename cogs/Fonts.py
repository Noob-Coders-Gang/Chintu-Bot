import json
import random
import discord
from discord.ext import commands

fonts = json.loads(open('./main_resources/Assets/fonts.json', 
                        encoding='utf-8').read())

def fontify(message: str, font: str):
    normal = str(fonts['normal'])

    if font == 'random':
        content = []
        for key, value in fonts.items():
            content.append(key)

        randtext = ""
        for letter in message:
            if letter not in normal:
                randtext += letter
                continue
        
            selected = fonts[random.choice(content)]
            i = normal.index(letter)
            randtext += selected[i]
        
        return randtext

    selected = str(fonts[font.lower()])

    text = ""
    for letter in message:
        if letter not in normal:
            text += letter
            continue
        i = normal.index(letter)
        text += selected[i]
    
    return text

class Fonts(commands.Cog):
    '''Custom Fonts Generator'''

    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="fontlist", aliases=['fonts'])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def fontlist(self, ctx):
        '''Display all Font List'''
        
        embed = discord.Embed(title="Fonts List",
                            color=discord.Colour.green())
        
        for key, value in fonts.items():
            if key == 'normal':
                continue
            embed.add_field(name=key, value=f"{value[0:3]}{value[26:29]}{value[52:55]}")
        
        embed.add_field(name="random", value="Random letters")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="font")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def font(self, ctx, type: str, *args):
        '''Change font and send'''

        if type in fonts or type == 'random':
            message = ""
            for i in args:
                message = message + " " + i
                message.strip()
            text = fontify(message, type)

            await ctx.send(text)
        
        else:
            embed = discord.Embed(title="**Error**", 
                                description="Write the proper font name noob",
                                color=discord.Colour.red())
            await ctx.send(embed=embed)
    
    
    
def setup(bot):
    bot.add_cog(Fonts(bot))
    
#------------------------------------------------------------#