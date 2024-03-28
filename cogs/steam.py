import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import requests

import tzlocal

import os
import settings as settings
logger = settings.logging.getLogger("bot")
steamKey = settings.STEAM_KEY

from datetime import datetime

class steam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    async def formatSteamProfileSummaries(self, profile):
        personaStatuses = {
        0: ["Offline", discord.Color.from_rgb(128,128,128)],
        1: ["Online", discord.Color.green()],
        2: ["Busy", discord.Color.red()],
        3: ["Away", discord.Color.yellow()],
        4: ["Snooze", discord.Color.orange()],
        5: ["Looking to trade",discord.Color.pink()],
        6: ["Looking to play", discord.Color.blue()]
        }

        if profile["communityvisibilitystate"] == 1:
            description = f"**{personaStatuses[profile['personastate']][0]}\nLast seen: {datetime.utcfromtimestamp(profile['lastlogoff']).strftime('%d-%m-%Y %H:%M:%S')}"
        elif "realname" in profile:
            description = f"**{profile['realname']}**\n{personaStatuses[profile['personastate']][0]}\nLast seen: {datetime.utcfromtimestamp(profile['lastlogoff']).strftime('%d-%m-%Y %H:%M:%S')}"
        else:
            description = f"{personaStatuses[profile['personastate']][0]}\nLast seen: {datetime.fromtimestamp(profile['lastlogoff'], tzlocal.get_localzone()).strftime('%d-%m-%Y %H:%M:%S')}"

        embed = discord.Embed(
            title = profile["personaname"],
            description = description,
            color = personaStatuses[profile['personastate']][1],
            url=profile["profileurl"]
        )

        #loops through profile dict to add any private data if exists.
        for key in profile:
            if key == "gameextrainfo":
                embed.add_field(name="Currently playing", value=profile[key], inline=False)
        
        embed.set_thumbnail(url=profile["avatarfull"])
        embed.set_footer(text=f"SteamID: {profile['steamid']}")

        return embed
    
    @app_commands.command(name="get_steam_profile", description="Get steam user info")
    @app_commands.describe(profile = "Copy and paste someone's profile id, or the link of their profile to get their profile!", user = "Get the steam profile of a discord user")
    async def getProfile(self, interaction:discord.Interaction, profile:str=None, user:discord.Member=None):
        await interaction.response.defer()

        if profile is None:
            with open("steamdetails.json", "r+") as file:
                file = file.read()
                steamdetails = json.load(file)
                try:
                    profile = steamdetails[str(user.id)]
                except KeyError:
                    return await interaction.followup.send("No profile found, either run /login_for_steam, or provide a profile as a parameter!", ephemeral=True)
        else:
            if "https://steamcommunity.com/profiles/" in profile:
                profile = profile.split("https://steamcommunity.com/profiles/")[1]
            elif "https://steamcommunity.com/id/" in profile:
                return await interaction.followup.send("Custom profile links aren't allowed, please provide their steamid instead!")
        
        response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steamKey}&steamids={profile}")
        response = response.json()

    #         print(json.dumps(response, indent=4))
    #         {
    #     "response": {
    #         "players": [
    #             {
    #                 "steamid": "76561198891750981",
    #                 "communityvisibilitystate": 3,
    #                 "profilestate": 1,
    #                 "personaname": "Fish_Man321",
    #                 "profileurl": "https://steamcommunity.com/profiles/76561198891750981/",
    #                 "avatar": "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb.jpg",
    #                 "avatarmedium": "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg",
    #                 "avatarfull": "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
    #                 "avatarhash": "fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb",
    #                 "lastlogoff": 1711589972,
    #                 "personastate": 0,
    #                 "realname": "Nathaniel",
    #                 "primaryclanid": "103582791429521408",
    #                 "timecreated": 1548315815,
    #                 "personastateflags": 0
    #             }
    #         ]
    #     }
    # }
        try:
            profile = response["response"]["players"][0]
        except IndexError:
            logger.info(f"Failed to find profile from {profile} with the response of {json.dumps(response, indent=4)}")
            return await interaction.followup.send("No profile found, please try again.")
        embed = await self.formatSteamProfileSummaries(profile)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="login_for_steam", description="Login to your steam account")
    @app_commands.describe(steamprofile = "Assign a steamid to your user.")
    async def loginForSteam(self, interaction:discord.Interaction, steamprofile:str):
        try:
            with open("steamdetails.json", "w+") as file:
                file = file.read()
                steamdetails:dict = json.loads(file)
                steamdetails.update({str(interaction.user.id): steamprofile})

                json.dump(steamdetails, file)

                return await interaction.response.send_message("Successfully assigned the steam profile to your user!", ephemeral=True)
        except Exception as e:
            logger.info(f"Failed to assign steam profile to user with the error: {e}")
            return await interaction.response.send_message("Failed to assign steam profile to your user!", ephemeral=True)
        

                
async def setup(bot):
    await bot.add_cog(steam(bot))