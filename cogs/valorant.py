import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import sys
import json

import settings as settings

valorant_api = settings.VALORANT_API

class Valorant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.slash_command(name="Get_recent_game", description="Get your recent game stats")
    async def getRecentGames(self, interaction: discord.Interaction):

        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)

            try:
                riotDetails = riotDetails[interaction.user.id]
            except Exception as e:
                return await interaction.response.send_message("Run /login before using this!", ephemeral=True)
                
            

    @app_commands.slash_command(name="Login", description="Login into your account")
    async def login(self, interaction:discord.Interaction, riotid:str):
        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)
        
        with open ("riotdetails.json", "w") as file:
            riotDetails[interaction.user.id] = {
                "id": riotid
            }
            json.dump(riotDetails, file)