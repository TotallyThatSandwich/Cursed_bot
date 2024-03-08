import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import sys
import json
import requests

import settings as settings

valorant_api = settings.VALORANT_API

class Valorant(commands.Cog):


    def __init__(self, bot):
        self.bot = bot

    def formatMessages(response, puuid):
        
        finalGameStats = {}
        
        matchDetails = response["data"][0]["metadata"]
        playerDetails = response["data"][0]["players"]["all_players"]
        teamDetails = response["data"][0]["teams"]

        for i in playerDetails:
            if i["puuid"] == puuid:
                requestedUser = i
                break
        
        totalRoundsPlayed = teamDetails["red"]["rounds_won"] + teamDetails["blue"]["rounds_won"]
        
        gameStats = {}

        for i in playerDetails:
            gameStats.update({"kills": i["stats"]["kills"],
                              "deaths": i["stats"]["deaths"],
                              "assists": i["stats"]["assists"],
                              "ACS": i["stats"]["score"]/totalRoundsPlayed,
                              "ADR": i["damage_made"]/totalRoundsPlayed,
                              "DD": (i["damage_made"]/totalRoundsPlayed)-(i["damage_received"]/totalRoundsPlayed),
                              "rank": i["currenttier_patched"],
                              "team": i["team"],
                              "HS": f"{i["stats"]["headshots"]/(i["stats"]["bodyshots"]+i["stats"]["headshots"]/i["stats"]["legshots"])*100}%",
                              "agent": i["character"],
                              "tag":i["tag"]}
                              )
            
            finalGameStats.update({i["name"]: gameStats})

        
        finalFormat = {
            "matchTitle": f"{teamDetails["red"]["rounds_won"]}:{teamDetails["blue"]["rounds_won"]}",
            "matchDescription": f"**{matchDetails["map"]} - {matchDetails["mode"]}**",
            "matchStats": f"**{requestedUser["stats"]["kills"]}/{requestedUser["stats"]["deaths"]}/{requestedUser["stats"]["assists"]}**",
            "agent": f"**{requestedUser["assets"]["agent"]["small"]}**",

        }
        return finalFormat

    @app_commands.slash_command(name="Get_recent_game", description="Get your recent game stats")
    async def getRecentGame(self, interaction: discord.Interaction):
        URL = "https://api.henrikdev.xyz"
        userAccount = {}

        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)

            if not(str(interaction.user.id) in riotDetails):
                return await interaction.response.send_message("You are not logged in!", ephemeral=True)
            
            userAccount = riotDetails[str(interaction.user.id)]

        fetchParameters = {
            "affinity": "ap",
            "puuid": userAccount["data"]["puuid"],
            "size": 1
        }

        response = await requests.get(url=f"{URL}/valorant/v3/by-puuid/lifetime/matches", params=fetchParameters)
        response = response.json()

        if(response.status != 200):
            return await interaction.response.send_message(f"Error with the status of {response.status}", ephemeral=True)
        
        self.formatMessages(response, userAccount["data"]["puuid"])
        
        embed = discord.Embed(title=f"", description="Here are your recent game stats", color=0x00ff00)

        
            
            

    @app_commands.slash_command(name="Login", description="Login into your account")
    @app_commands.describe(riotid = "Enter your Riot ID. If you leave it empty, it will delete your information.")
    async def login(self, interaction:discord.Interaction, riotid:str, tag:int):
        if(riotid == None):
            with open("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.pop(str(interaction.user.id))
                with open("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)
            
            return await interaction.response.send_message("Deleting your information...", ephemeral=True, delete_after=10)
        
        fetchRequests = {
            "name": riotid,
            "tag": str(tag)
        }

        response = await requests.get(url="https://henrikdev.xyz/valorant/v1/account", params=fetchRequests)
        response = response.json()

        if(response.status != 200):
            return await interaction.response.send_message(f"Invalid Riot ID or Tag with the error of {response.status}", ephemeral=True)

        riotDetails = {}
        #opens the file and reads the json
        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)

        #opens the file and writes the json
        with open ("riotdetails.json", "w") as file:
            riotDetails.update({str(interaction.user.id): response})
            json.dump(riotDetails, file)
        
        await interaction.response.send_message("Logged in!", ephemeral=True)