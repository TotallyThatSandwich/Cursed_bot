import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import asyncio
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageChops
import urllib.request

import settings as settings
logger = settings.logging.getLogger("bot")




class valorant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    

    def formatMatchEmbed(self, response, puuid):
       
        finalGameStats = {}
        
        #assigns details from response JSON file acquired from match 
        matchDetails = response["data"][0]["metadata"]
        playerDetails = response["data"][0]["players"]["all_players"]
        teamDetails = response["data"][0]["teams"]
            
        
        totalRoundsPlayed = teamDetails["red"]["rounds_won"] + teamDetails["blue"]["rounds_won"]
        
        gameStats = {}

        for i in playerDetails:
            if i["puuid"] == puuid:
                requestedUser = i
            gameStats = {}
            gameStats.update({"team": i["team"],
                            "kills": i["stats"]["kills"], #int
                            "deaths": i["stats"]["deaths"], #int
                            "assists": i["stats"]["assists"], #int
                            "KDA": f'{i["stats"]["kills"]}/{i["stats"]["deaths"]}/{i["stats"]["assists"]}', #string
                            "KDR": i["stats"]["kills"]/i["stats"]["deaths"], #float
                            "ACS": round((i["stats"]["score"]/totalRoundsPlayed), 2), #float
                            "ADR": round((i["damage_made"]/totalRoundsPlayed),2), #float
                            "DD": math.floor((i["damage_made"]/totalRoundsPlayed)-(i["damage_received"]/totalRoundsPlayed)), #float -> int
                            "rank": i["currenttier_patched"], #string
                            "team": i["team"], #string
                            "HS": f'{i["stats"]["headshots"]/(i["stats"]["bodyshots"]+i["stats"]["headshots"]+i["stats"]["legshots"])*100}%', #string because of % sign
                            "agent": i["character"], #string
                            "tag":i["tag"], #string
                            "agentPfp": i["assets"]["agent"]["small"] #string
                            })
            
            finalGameStats.update({i["name"]: gameStats})
        
        print(json.dumps(finalGameStats, indent=4))
        personalUserStats = finalGameStats[requestedUser["name"]]

        self.createUserStatsImage(matchDetails["map"], personalUserStats["agentPfp"], personalUserStats, {"Red": teamDetails["red"]["rounds_won"], "Blue": teamDetails["blue"]["rounds_won"]})

    # function for creating an image to show your personal stats. Parameters are the map loading screen link, the agent picture link and the user stats
    def createUserStatsImage(self, map:str, agentPfp:str, userStats:dict, score:dict):
        mapLoadScreens = {
            "Ascent": "https://static.wikia.nocookie.net/valorant/images/e/e7/Loading_Screen_Ascent.png/revision/latest/scale-to-width-down/1000?cb=20200607180020",
            "Breeze": "https://static.wikia.nocookie.net/valorant/images/1/10/Loading_Screen_Breeze.png/revision/latest/scale-to-width-down/1200?cb=20210427160616",
            "Bind": "https://static.wikia.nocookie.net/valorant/images/2/23/Loading_Screen_Bind.png/revision/latest/scale-to-width-down/1200?cb=20200620202316",
            "Haven": "https://static.wikia.nocookie.net/valorant/images/7/70/Loading_Screen_Haven.png/revision/latest?cb=20200620202335",
            "Split":"https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png/revision/latest?cb=20230411161807",
            "Pearl":"https://static.wikia.nocookie.net/valorant/images/a/af/Loading_Screen_Pearl.png/revision/latest?cb=20220622132842",
            "Lotus": "https://static.wikia.nocookie.net/valorant/images/d/d0/Loading_Screen_Lotus.png/revision/latest?cb=20230106163526",
            "Fracture": "https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png/revision/latest?cb=20210908143656", 
            "Sunset": "https://static.wikia.nocookie.net/valorant/images/5/5c/Loading_Screen_Sunset.png/revision/latest?cb=20230829125442",
            "Icebox": "https://static.wikia.nocookie.net/valorant/images/1/13/Loading_Screen_Icebox.png/revision/latest/scale-to-width-down/1000?cb=20201015084446"
        }

        if userStats["team"] == "Red":
            scoreboard = f"{score['Red']} - {score['Blue']}"
        else:
            scoreboard = f"{score['Blue']} - {score['Red']}"

        mapLink = mapLoadScreens[map]
        urllib.request.urlretrieve(mapLink, "map.png")
        urllib.request.urlretrieve(agentPfp, "agentPfp.png")

        img = Image.new('RGB', (600, 300), color = (6, 9, 23))
        draw = ImageDraw.Draw(img)

        fnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=20)
        boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=45)


        #Draws the map image cropped on the top of the image
        mapImage = Image.open("map.png")
        mapImage = mapImage.resize([1200, 654])
        mapImage = ImageChops.offset(mapImage, 0, math.floor((mapImage.height)/2+100))
        mapImage = mapImage.crop((0,0, mapImage.width, 100))
        img.paste(mapImage, (0,0))
        
        #Draw the line dividing map image with stats
        draw.line([(0,100),(img.width,100)], fill=(0,0,0), width=15)

        #Paste agent picture on the left side of the image
        agentProfilePicture = Image.open("agentPfp.png")
        agentProfilePicture = agentProfilePicture.resize([200,200])
        img.paste(agentProfilePicture, (0,108))

        #Place player stats on the right of the agent picture
        draw.rectangle([(agentProfilePicture.width + 10, img.width), (666, img.width)],fill=(0,0,0), outline=(33, 38, 46))
        draw.text((agentProfilePicture.width + 20, 110), f"{scoreboard}", fill=(255,255,255), font=boldfnt)
        #KDA
        draw.text((agentProfilePicture.width + 20, 190), "KDA", fill=(255,255,255), font=fnt)
        draw.text((agentProfilePicture.width + 70, 190), f'{userStats["KDA"]}', fill=(255,255,255), font=fnt)
        #ADR
        draw.text((agentProfilePicture.width + 20, 220), "ADR", fill=(255,255,255), font=fnt)
        draw.text((agentProfilePicture.width + 70, 220), f'{userStats["ADR"]}', fill=(255,255,255), font=fnt)
        #ACS
        draw.text((agentProfilePicture.width + 20, 250), "ACS", fill=(255,255,255), font=fnt)
        draw.text((agentProfilePicture.width + 70, 250), f'{userStats["ACS"]}', fill=(255,255,255), font=fnt)

        img.save("userStats.png")
        os.remove("map.png")
        os.remove("agentPfp.png")

    @app_commands.command(name="get_latest_comp_game", description="Get your recent game stats")
    async def getRecentGame(self, interaction: discord.Interaction):
        await interaction.response.defer()
        URL = "https://api.henrikdev.xyz"
        userAccount = {}

        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)
            if not(str(interaction.user.id) in riotDetails):
                return await interaction.followup.send("You are not logged in!", ephemeral=True)

            userAccount = riotDetails[str(interaction.user.id)]

        

        fetchParameters = {
            "affinity": "ap",
            "puuid": userAccount["data"]["puuid"],
            "mode": "competitive",
            "size": 1
        }

        response = requests.get(url=f"{URL}/valorant/v3/by-puuid/matches/ap/{fetchParameters['puuid']}?mode={fetchParameters['mode']}&size={fetchParameters['size']}")
        response = response.json()

        if(response["status"] != 200):
            return await interaction.response.send_message(f"Error with the status of {response['status']}", ephemeral=True)

        self.formatMatchEmbed(response, userAccount["data"]["puuid"])
        
        userStatsFile = discord.File("userStats.png", filename="userStats.png")
        
        await interaction.followup.send(file=userStatsFile)
        os.remove("userStats.png")
        


    @app_commands.command(name="login_for_valorant", description="Login into your account")
    @app_commands.describe(username = "Enter your Valorant username. If you leave it empty, it will delete your information.")
    async def login(self, interaction:discord.Interaction, username:str, tag:int):
        if(username == None):
            with open("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.pop(str(interaction.user.id))
                with open("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)
            
            return await interaction.response.send_message("Deleting your information...", ephemeral=True, delete_after=10)
        
        fetchRequests = {
            "name": username,
            "tag": str(tag)
        }

        response = requests.get(url=f"https://api.henrikdev.xyz/valorant/v1/account/{fetchRequests['name']}/{fetchRequests['tag']}")
        response = response.json()

        print("\n"+str(response)+"\n")

        if(response["status"] != 200):
            return await interaction.response.send_message(f"Invalid Riot ID or Tag with the error of {response['status']}", ephemeral=True)

        riotDetails = {}
        try:
        #opens the file and reads the json
            with open ("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.update({str(interaction.user.id): response})
                with open ("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)

        except Exception as e:
            
            with open ("riotdetails.json", "w+") as file:
                riotDetails.update({str(interaction.user.id): response})
                json.dump(riotDetails, file)
        
        await interaction.response.send_message("Logged in!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(valorant(bot))