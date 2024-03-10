import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import requests

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageChops
import urllib.request

import settings as settings
logger = settings.logging.getLogger("bot")

class discordUI(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="Scoreboard", style=discord.ButtonStyle.blurple, custom_id="scoreboardswap")
    async def scoreboard(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(attachments=[discord.File(f"gameStats{interaction.message.id}.png")], delete_after=600)

    @discord.ui.button(label="Personal", style=discord.ButtonStyle.blurple, custom_id="personalswap")
    async def personal(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(attachments=[discord.File(f"userStats{interaction.message.id}.png")], delete_after=600)



class valorant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        print("deleted", str(message.id))
        messageID = str(message.id)

        with open("recentGames.txt", "r") as file:
            recentGames = file.readline()
            recentGames = recentGames.replace(" ", "")
            recentGames = recentGames.split(",")
            
            # not sure why reading lines include the \n as a part of the string?
            print("finding " + messageID + " in " + str(recentGames))
            if messageID in recentGames:
                recentGames = recentGames.remove(messageID)
                print("removing", f"userStats{message.id}.png and gameStats{message.id}.png")
                os.remove(f"userStats{message.id}.png")
                os.remove(f"gameStats{message.id}.png")
                
                with open("recentGames.txt", "a+") as file:
                    for i in recentGames:
                        file.write(f" {i},")

    def formatMatchEmbed(self, messageid, response=None, puuid=None):       
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
                            "HS": f'{round((i["stats"]["headshots"]/(i["stats"]["bodyshots"]+i["stats"]["headshots"]+i["stats"]["legshots"])*100),2)}%', #string because of % sign
                            "agent": i["character"], #string
                            "tag":i["tag"], #string
                            "agentPfp": i["assets"]["agent"]["small"] #string
                            })
            
            finalGameStats.update({i["name"]: gameStats})
        
        print(json.dumps(finalGameStats, indent=4))
        personalUserStats = finalGameStats[requestedUser["name"]]

        self.createUserStatsImage(matchDetails["map"], personalUserStats["agentPfp"], personalUserStats, {"Red": teamDetails["red"]["rounds_won"], "Blue": teamDetails["blue"]["rounds_won"]}, messageid)
        self.createTotalGameStatsImage(matchDetails["map"], finalGameStats, {"Red": teamDetails["red"]["rounds_won"], "Blue": teamDetails["blue"]["rounds_won"]}, messageid)

    # function for creating an image to show the stats of the game. Parameters are the map name, the stats of the players and the score of the game
    def createTotalGameStatsImage(self, map:str, stats:dict, score:dict, messageId):
        mapLoadScreens = {
            "Ascent": "https://static.wikia.nocookie.net/valorant/images/e/e7/Loading_Screen_Ascent.png/revision/latest?cb=20200607180020",
            "Breeze": "https://static.wikia.nocookie.net/valorant/images/1/10/Loading_Screen_Breeze.png/revision/latest",
            "Bind": "https://static.wikia.nocookie.net/valorant/images/2/23/Loading_Screen_Bind.png/revision/latest",
            "Haven": "https://static.wikia.nocookie.net/valorant/images/7/70/Loading_Screen_Haven.png/revision/latest?cb=20200620202335",
            "Split":"https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png/revision/latest?cb=20230411161807",
            "Pearl":"https://static.wikia.nocookie.net/valorant/images/a/af/Loading_Screen_Pearl.png/revision/latest?cb=20220622132842",
            "Lotus": "https://static.wikia.nocookie.net/valorant/images/d/d0/Loading_Screen_Lotus.png/revision/latest?cb=20230106163526",
            "Fracture": "https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png/revision/latest?cb=20210908143656", 
            "Sunset": "https://static.wikia.nocookie.net/valorant/images/5/5c/Loading_Screen_Sunset.png/revision/latest?cb=20230829125442",
            "Icebox": "https://static.wikia.nocookie.net/valorant/images/1/13/Loading_Screen_Icebox.png/revision/latest"
        }

        scoreLine = f"{score['Blue']} - {score['Red']}"
        mapLink = mapLoadScreens[map]
        urllib.request.urlretrieve(mapLink, "map.png")

        img = Image.new('RGB', (800, 1200), color = (6, 9, 23))
        draw = ImageDraw.Draw(img)

        fnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=15)
        boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=80)

        def sortLowestToHighest(arr, stat):
            length = len(arr)

            for i in range(length):
                for j in range(0, length):
                    print(str(i), str(j))
                    print(f"i: {str(arr[i])} {str(stats[arr[i]]['ACS'])}, j: {str(arr[j])} {str(stats[arr[j]]['ACS'])}")
                    
                    if stats[arr[i]][stat] > stats[arr[j]][stat]:
                        print(f"Swapping {arr[i]} with {arr[j]}")
                        arr[i], arr[j] = arr[j], arr[i]
            
            return arr

        #start by dividing characters into their teams, then sorting by ACS, then draw the characters in their respective teams, with their stats
        red_team = []
        blue_team = []
        for i in stats:
            if stats[i]["team"] == "Red":
                red_team.append(i)
            else:
                blue_team.append(i)

        blueTeamPlayerCount = len(blue_team)
        redTeamPlayerCount = len(red_team)
        totalPlayerCount = blueTeamPlayerCount + redTeamPlayerCount

        blue_team = sortLowestToHighest(blue_team, "ACS")
        red_team = sortLowestToHighest(red_team, "ACS")

        #Draws the map image cropped on the top of the image
        mapImage = Image.open("map.png")
        mapImage = mapImage.resize([1200, 654])
        mapImage = ImageChops.offset(mapImage, math.floor((mapImage.width)/2+100), math.floor((mapImage.height)/2+100))
        mapImage = mapImage.crop((0,0, mapImage.width, 100))
        img.paste(mapImage, (0,0))

        # Draw the line dividing map image with stats
        draw.line([(0,100),(img.width,100)], fill=(33,38,46), width=15)

        # from left to right, label stats
        # agentPfp, username:tag, rank, KDA, ACS, ADR, HS%, DD
        draw.rectangle([(img.width, 100), (img.width, 110)],fill=(0,0,0), outline=(33, 38, 46))
        draw.text((img.width/2, mapImage.height/2), scoreLine, font=boldfnt, fill=(0,0,0),stroke_fill=(255,255,255), stroke_width=1,anchor="mm")

        draw.text((300, 130), "KDA", font=fnt, fill=(255,255,255))
        draw.text((400, 130), "ACS", font=fnt, fill=(255,255,255))
        draw.text((500, 130), "ADR", font=fnt, fill=(255,255,255))
        draw.text((600, 130), "HS%", font=fnt, fill=(255,255,255))
        draw.text((700, 130), "DD", font=fnt, fill=(255,255,255))

        for i in range(blueTeamPlayerCount):
            #draw agent pfp
            urllib.request.urlretrieve(stats[blue_team[i]]["agentPfp"], f"agentPfp{i}.png")
            agentPfp = Image.open(f"agentPfp{i}.png")
            agentPfp = agentPfp.resize([100, 100])
            img.paste(agentPfp, (0, 150+(i*100)))

            #draw username:tag
            if(len(blue_team[i]) > 12):
                name = str(blue_team[i][:12]) + "..."
            else:
                name = blue_team[i]
            draw.text((105, 170+(i*100)), f"{name}: {stats[blue_team[i]]['tag']}", font=fnt, fill=(255,255,255))

            #draw rank
            draw.text((105, 190+(i*100)), f"{stats[blue_team[i]]['rank']}", font=fnt, fill=(255,255,255))

            #draw KDA
            draw.text((300, 170+(i*100)), f"{stats[blue_team[i]]['KDA']}", font=fnt, fill=(255,255,255))

            #draw ACS
            draw.text((400, 170+(i*100)), f"{stats[blue_team[i]]['ACS']}", font=fnt, fill=(255,255,255))

            #draw ADR
            draw.text((500, 170+(i*100)), f"{stats[blue_team[i]]['ADR']}", font=fnt, fill=(255,255,255))

            #draw HS%
            draw.text((600, 170+(i*100)), f"{stats[blue_team[i]]['HS']}", font=fnt, fill=(255,255,255))

            #draw DD
            draw.text((700, 170+(i*100)), f"{stats[blue_team[i]]['DD']}", font=fnt, fill=(255,255,255))

        draw.line([(0,150+(blueTeamPlayerCount*100)),(img.width,150+(blueTeamPlayerCount*100))], fill=(33,38,46), width=5)
        draw.rectangle([(img.width, 150+(blueTeamPlayerCount*100)), (img.width, 150+(blueTeamPlayerCount*100))],fill=(59, 19, 19), outline=(33, 38, 46))
        for i in range(redTeamPlayerCount):
            urllib.request.urlretrieve(stats[red_team[i]]["agentPfp"], f"agentPfp{i+6}.png")
            agentPfp = Image.open(f"agentPfp{i+6}.png")
            agentPfp = agentPfp.resize([100, 100])
            img.paste(agentPfp, (0, 650+(i*100)))

            #draw username:tag
            if(len(red_team[i]) > 12):
                name = str(red_team[i][:12]) + "..."
            else:
                name = red_team[i]
            draw.text((105, 670+(i*100)), f"{name}:#{stats[red_team[i]]['tag']}", font=fnt, fill=(255,255,255))

            #draw rank
            draw.text((105, 690+(i*100)), f"{stats[red_team[i]]['rank']}", font=fnt, fill=(255,255,255))

            #draw KDA
            draw.text((300, 670+(i*100)), f"{stats[red_team[i]]['KDA']}", font=fnt, fill=(255,255,255))

            #draw ACS
            draw.text((400, 670+(i*100)), f"{stats[red_team[i]]['ACS']}", font=fnt, fill=(255,255,255))

            #draw ADR
            draw.text((500, 670+(i*100)), f"{stats[red_team[i]]['ADR']}", font=fnt, fill=(255,255,255))

            #draw HS%
            draw.text((600, 670+(i*100)), f"{stats[red_team[i]]['HS']}", font=fnt, fill=(255,255,255))

            #draw DD
            draw.text((700, 670+(i*100)), f"{stats[red_team[i]]['DD']}", font=fnt, fill=(255,255,255))


        img.save(f"gameStats{messageId}.png")
        os.remove("map.png")
        for i in range(totalPlayerCount):
            try:
                os.remove(f"agentPfp{i}.png")
            except:
                continue


    # function for creating an image to show your personal stats. Parameters are the map name, the agent picture link, user stats and the score in the format of {"Red": 0, "Blue": 0}
    def createUserStatsImage(self, map:str, agentPfp:str, userStats:dict, score:dict, messageId):
        mapLoadScreens = {
            "Ascent": "https://static.wikia.nocookie.net/valorant/images/e/e7/Loading_Screen_Ascent.png/revision/latest?cb=20200607180020",
            "Breeze": "https://static.wikia.nocookie.net/valorant/images/1/10/Loading_Screen_Breeze.png/revision/latest",
            "Bind": "https://static.wikia.nocookie.net/valorant/images/2/23/Loading_Screen_Bind.png/revision/latest",
            "Haven": "https://static.wikia.nocookie.net/valorant/images/7/70/Loading_Screen_Haven.png/revision/latest?cb=20200620202335",
            "Split":"https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png/revision/latest?cb=20230411161807",
            "Pearl":"https://static.wikia.nocookie.net/valorant/images/a/af/Loading_Screen_Pearl.png/revision/latest?cb=20220622132842",
            "Lotus": "https://static.wikia.nocookie.net/valorant/images/d/d0/Loading_Screen_Lotus.png/revision/latest?cb=20230106163526",
            "Fracture": "https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png/revision/latest?cb=20210908143656", 
            "Sunset": "https://static.wikia.nocookie.net/valorant/images/5/5c/Loading_Screen_Sunset.png/revision/latest?cb=20230829125442",
            "Icebox": "https://static.wikia.nocookie.net/valorant/images/1/13/Loading_Screen_Icebox.png/revision/latest"
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
        mapImage = ImageChops.offset(mapImage, math.floor((mapImage.width)/2+100), math.floor((mapImage.height)/2+100))
        mapImage = mapImage.crop((0,0, mapImage.width, 100))
        img.paste(mapImage, (0,0))
        
        #Draw the line dividing map image with stats
        #draw.line([(0,100),(img.width,100)], fill=(0,0,0), width=15)

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

        img.save(f"userStats{messageId}.png")
        os.remove("map.png")
        os.remove("agentPfp.png")
    
    @app_commands.command(name="get_latest_comp_game", description="Get your recent game stats")
    @app_commands.describe(user = "Grab user's latest game. Optional.")
    async def getRecentGame(self, interaction: discord.Interaction, user:discord.Member=None):
        await interaction.response.defer()
        message = await interaction.original_response()
        URL = "https://api.henrikdev.xyz"
        userAccount = {}

        with open ("riotdetails.json", "r") as file:
            riotDetails = json.load(file)

            if str(interaction.user.id) not in riotDetails and user == None:
                return await interaction.followup.send("Run /login_for_valorant before running this command!", ephemeral=True)
            
            if user != None and str(user.id) not in riotDetails:
                return await interaction.followup.send("User has not logged in yet! They must run /login_for_valorant before trying this command", ephemeral=True)
            
            if user == None:
                userAccount = riotDetails[str(interaction.user.id)]
            else:
                userAccount = riotDetails[str(user.id)]
            

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

        self.formatMatchEmbed(message.id, response, userAccount["data"]["puuid"],)
        
        userStatsFile = discord.File(f"userStats{message.id}.png", filename=f"userStats{message.id}.png")
        gameStatsFile = discord.File(f"gameStats{message.id}.png", filename=f"gameStats{message.id}.png")
        
        await interaction.followup.send(file=userStatsFile, view=discordUI())
        
        await message.edit(delete_after=600)
        message = message.id

        with open("recentGames.txt", "a+") as file:
            file.write(f" {message},")
        
        
        
    @app_commands.command(name="login_for_valorant", description="Login into your account")
    @app_commands.describe(username = "Enter your Valorant username. If you leave it empty, it will delete your information.")
    async def loginValorant(self, interaction:discord.Interaction, username:str, tag:str):
        if(username == None):
            with open("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.pop(str(interaction.user.id))
                with open("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)
            
            return await interaction.response.send_message("Deleting your information...", ephemeral=True, delete_after=10)
        
        
        if("#" in str(tag)):
            tag = tag.replace("#", "")
        
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
                    
            await interaction.response.send_message("Logged in!", ephemeral=True)
        except Exception as e:
            with open ("riotdetails.json", "w+") as file:
                riotDetails.update({str(interaction.user.id): response})
                json.dump(riotDetails, file)
        
            await interaction.response.send_message("Logged in!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(valorant(bot))