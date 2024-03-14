import discord
from discord.ext import commands
from discord import app_commands
import requests

class Helldivers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Helldivers cog is ready.')

    @commands.command(name="get_latest_comp_game", description="Get your recent game stats")
    async def hello(self, interaction: discord.Interaction):

        response = requests.get("https://helldivers-2.fly.dev/api/801/planets")
        if response.status_code == 200:
            planets = response.json()
            
            for i in planets:

                index = i["index"]

        else:
            print("Failed to fetch planets data")

def setup(bot):
    bot.add_cog(Helldivers(bot))