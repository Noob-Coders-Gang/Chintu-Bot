import discord
import json
import requests
from discord.ext import commands




class Pokemon(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pokedex(self, ctx, *args):
        url = requests.get('https://pokeapi.co/api/v2/pokemon/{}'.format(' '.join(args)))
        data = url.json()
        em = discord.Embed(
            title=data['name']
        )
        em.set_image(url=data['sprites']['front_default'])
        em.add_field(name="ID", value=data['id'], inline=False)
        em.add_field(name="Base XP", value=data['base_experience'], inline=False)
        em.add_field(name="Height", value=data['height'], inline=False)
        em.add_field(name="HP", value=data['stats'][0]['base_stat'])
        em.add_field(name="Attack", value=data['stats'][1]['base_stat'])
        em.add_field(name="Defense", value=data['stats'][2]['base_stat'])
        em.add_field(name="SP.Atk", value=data['stats'][3]['base_stat'])
        em.add_field(name="SP.Def", value=data['stats'][4]['base_stat'])
        em.add_field(name="Speed", value=data['stats'][5]['base_stat'])
        for i in range(0, 2):
            em.add_field(name="Ability", value=data['abilities'][i]['ability']['name'], inline=False)
        
        await ctx.send(embed=em)


def setup(client):
    client.add_cog(Pokemon(client))




