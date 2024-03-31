from typing import Coroutine
import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import requests

from asyncio import sleep

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageChops
import urllib.request

import settings as settings
logger = settings.logging.getLogger("bot")

class matchStatsUI(discord.ui.View):
    def __init__(self):
        super().__init__(),
        self.children[1].disabled = True
    
    @discord.ui.button(label="Scoreboard", style=discord.ButtonStyle.blurple, custom_id="scoreboardswap")
    async def scoreboard(self, interaction:discord.Interaction, button:discord.ui.Button):
        for i in self.children:
            if i.disabled == False:
                i.disabled = True
            else:
                i.disabled = False
        await interaction.response.edit_message(attachments=[discord.File(f"gameStats{interaction.message.id}.png")], delete_after=600, view=self)
        

    @discord.ui.button(label="Personal", style=discord.ButtonStyle.blurple, custom_id="personalswap")
    async def personal(self, interaction:discord.Interaction, button:discord.ui.Button):
        for i in self.children:
            if i.disabled == False:
                i.disabled = True
            else:
                i.disabled = False
        await interaction.response.edit_message(attachments=[discord.File(f"userStats{interaction.message.id}.png")], delete_after=600, view=self)
        

class selectMatchUI(discord.ui.View):
    def __init__(self, options=None):
        super().__init__()

    @discord.ui.select(placeholder="Select a match")
    async def matchHistoryCallback(self, interaction:discord.Interaction, select:discord.ui.Select):
        await interaction.response.defer()
        matchStats = valorant.matchStats[int(str(select.values[0]).lstrip("Match "))-1]
        userAccount = valorant.userAccount
        try:
            valorant.formatMatchEmbed(interaction.message.id, [matchStats[0], matchStats[1], matchStats[2]],userAccount["data"]["puuid"])
            with open("recentGames.txt", "a+") as file:
                file.write(f"{interaction.message.id},")
            
            await interaction.followup.edit_message(interaction.message.id, attachments=[discord.File(f"userStats{interaction.message.id}.png")], view=matchStatsUI())
        except TypeError as e:
            print(e)
        

class valorant(commands.Cog):

    def __init__(self, bot, matchStats, userAccount):
        self.bot = bot,
        self.matchStats = matchStats, # matchStats is a list of the match data in the format of [matchDetails, playerDetails, teamDetails]
        self.userAccount = userAccount # userAccount is the user's account details from the API

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
                recentGames.remove(messageID)
                print("removing", f"userStats{message.id}.png and gameStats{message.id}.png")
                os.remove(f"userStats{message.id}.png")
                os.remove(f"gameStats{message.id}.png")
                
                with open("recentGames.txt", "w") as file:
                    file.write("")

                    with open("recentGames.txt", "a+") as file:
                        for i in recentGames:
                            if i != "":
                                file.write(f" {i},")
        
    def getLengthAndHeightOfText(self, text:str, font:str, fontsize:int):
        fnt = ImageFont.truetype(font=font, size=fontsize)
        canvas = Image.new('RGB', (1000,1000))
        canvasDraw = ImageDraw.Draw(canvas)
        canvasDraw.text((10,10), text, font=fnt, fill=(255,255,255))
        bbox = canvas.getbbox()

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        print("bbox:", str(bbox), "width:", str(width), "height:", str(height))

        return width, height
    
    #SECTION: Get a large widescreen of user stats           
    def createValorantAccountImage(self, accountInfo:dict, matchStats:dict, averagedStats:dict,gameStats:dict, otherStats:dict):

        img = Image.new('RGBA', (1920, 910), color = (6, 9, 23))
        draw = ImageDraw.Draw(img, "RGBA")

        fnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=65)
        subfnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=40)
        userfnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=30)

        username = accountInfo['data']['name']

        if len(username) <6:
            boldFntSize = 100
            boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=100)
        else:
            boldFntSize = 100-((len(username)-6)*15)
            boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=100-((len(username)-6)*15))

        #Most played agent image
        agentName = otherStats["mostPlayedAgent"]["agentName"]
        for i in agentName:
            if str(i).isalpha() == False:
                agentName = agentName.replace(i, "")
        mostPlayedAgent = Image.open(f"images/valorantAgents/{agentName}.png")
        mostPlayedAgent = ImageChops.offset(mostPlayedAgent, -250, 0)
        mostPlayedAgent = mostPlayedAgent.crop(((0,0,600,910)))
    
        img.paste(mostPlayedAgent, (0,0))

        width, height = self.getLengthAndHeightOfText(f"{accountInfo['data']['name']}", "fonts/OpenSans-Bold.ttf", boldFntSize)
        draw.text([605, 0], f"{accountInfo['data']['name']}", font=boldfnt, fill=(255,255,255))
        draw.text([605+(width+20), 30], f"#{accountInfo['data']['tag']}", font=subfnt, fill=(255,255,255))
        draw.text([605+(width+20), 60], f"{accountInfo['data']['region']}", font=subfnt, fill=(255,255,255))
        
        #Draw rectange to contain account info like rank, level and tier
        rank = gameStats[0]["rank"]
        rank = rank.replace(" ", "_")
        rank += "_Rank"

        rankImage = Image.open(f"images/valorantRanks/{rank}.png")
        rankImageBckg = Image.new("RGBA", rankImage.size, color=(6, 9, 23))
        rankImageBckg.paste(rankImage, (0,0), mask = rankImage)
        rankImageBckg.convert("RGB").save("rankImage.jpg")
        rankImage = Image.open("rankImage.jpg")
        rankImage = rankImage.resize([280, 280])
        img.paste(rankImage, (615, 160))
    
    
        draw.text([900, 220], f"Level", font=fnt, fill=(255,255,255))
        width, height = self.getLengthAndHeightOfText(f"Level", "fonts/OpenSans-Regular.ttf", 65)
        draw.text([900, 220+height+30], f"{accountInfo['data']['account_level']}", font=subfnt, fill=(255,255,255), align="left")

        # Draw average stats in the last ten games
        width, height = self.getLengthAndHeightOfText("ADR", "fonts/OpenSans-Regular.ttf", 65)
        for i in range(len(averagedStats)):
            draw.text([620,550+(i*(height+25))], f"{list(averagedStats.keys())[i]}", font=subfnt, fill=(156, 156, 156))
            draw.text([700, 550+((i*(height+25))+(height/2))], f"{list(averagedStats.values())[i]}", font=fnt, fill=(255,255,255))
    
        # Draw the line dividing average stats and match history, then draw match history
        draw.line([(1200, 0), (1200, img.height)], fill=(256,256,256), width=5)
        matchFnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=25)
        for i in range(len(gameStats)):
            game = gameStats[i]
            scoreline = game["matchDetails"]["playerSidedScore"]
            scoreline = scoreline.split(" - ")
            if int(scoreline[0]) > int(scoreline[1]):
                win = True
            elif int(scoreline[0]) < int(scoreline[1]):
                win = False
            else:
                win = None

            urllib.request.urlretrieve(game["agentPfp"], f"agentPfp{i}.png")
            agentPfp = Image.open(f"agentPfp{i}.png")
            agentPfp = agentPfp.resize([200,200])

            if win:
                agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(3, 54, 8))
            elif win == False:
                agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(43, 2, 6))
            else:
                agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(125, 120, 24))
            
            agentPfpBckg.paste(agentPfp, (0,0), mask = agentPfp)
            agentPfpBckg.convert("RGB").save(f"agentPfp{i}.jpg")
            agentPfp = Image.open(f"agentPfp{i}.jpg")
            agentPfp = agentPfp.resize([91,91])
            img.paste(agentPfp, (1210, 0+(i*91)))

            os.remove(f"agentPfp{i}.png")
            os.remove(f"agentPfp{i}.jpg")

            if win:
                draw.rectangle([(1200, 0+(i*91)), (1210, 200+(i*91))], fill=(0,255,0))
                draw.rounded_rectangle([(1301, 0+(i*91)), (1920, 200+(i*91))], fill=(3, 54, 8), radius= 2)
            elif win == False:
                draw.rectangle([(1200, 0+(i*91)), (1210, 200+(i*91))], fill=(255,0,0))
                draw.rounded_rectangle([(1301, 0+(i*91)), (1920, 200+(i*91))], fill=(43, 2, 6), radius= 2)
            else:
                draw.rectangle([(1200, 0+(i*91)), (1210, 200+(i*91))], fill=(255, 255, 0))
                draw.rounded_rectangle([(1301, 0+(i*91)), (1920, 200+(i*91))], fill=(125, 120, 24), radius= 2)

            draw.text([1309, 0+(i*91)], f"{game['matchDetails']['map']}\n{game['matchDetails']['playerSidedScore']}", font=matchFnt, fill=(255,255,255))
        
        img.save("valorantAccountStats.png")
        os.remove("rankImage.jpg")


        
    
    @app_commands.command(name="valorant_account_summary", description="Your total game stats from your past 10 competitive games")
    @app_commands.describe(user="Get user's account stats", riotuser="Get stats from Riot user instead of Discord user. A Riot tag must be provided as well", refresh="Refresh your acccount stats")
    async def getUserAccount(self, interaction:discord.Interaction, user:discord.Member=None, riotuser:str=None, riottag:str=None, refresh:bool=False):
        await interaction.response.defer()
        message = await interaction.original_response()

        if not os.path.exists("riotdetails.json"):
            print(os.path.exists("riotdetails.json"))
            return await interaction.followup.send("Run /login_for_valorant before running this command!", ephemeral=True)

        if user == None:
            print("using interaction user id")
            userId = str(interaction.user.id)
        else:
            print("using user id")
            userId = str(user.id)
    
        if riotuser == None:
            if refresh == True:
                targetAccount = self.refreshLoginForValorantDetails(userId)
            else:
                with open("riotdetails.json", "r") as file:
                        try:
                            riotDetails = json.load(file)
                            print(userId)
                            targetAccount = riotDetails[userId]
                        except Exception as e:
                            print(e)
                            return await interaction.followup.send("User has not logged in yet! They must run /login_for_valorant before trying this command", ephemeral=True)
        else:
            if riottag == None:
                return await interaction.followup.send("Please provide a riot tag", ephemeral=True)
            
            targetAccount = requests.get(url=f"https://api.henrikdev.xyz/valorant/v1/account/{riotuser}/{riottag}")
            targetAccount = targetAccount.json()
            

        print("target account:", str(targetAccount))
        region = targetAccount["data"]["region"]
        response = requests.get(url=f"https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/{region}/{targetAccount['data']['puuid']}?mode=competitive&size=10")
        response = response.json()
        if response["status"] != 200:
            return await interaction.followup.send(f"Error with the status of {response['status']}", ephemeral=True)

        try:
            userStatsFromMatchHistory = await self.calculateUserStatsFromGames(response, targetAccount)
            matchStats = userStatsFromMatchHistory["matchStats"]
            averagedStats = userStatsFromMatchHistory["averagedStats"]
            otherStats = userStatsFromMatchHistory["otherStats"]
            gameStats = userStatsFromMatchHistory["gameStats"]
        except TypeError:
            return await interaction.followup.send("Failure! Stats are unfetchable.", ephemeral=True)

        self.createValorantAccountImage(targetAccount, matchStats, averagedStats, gameStats, otherStats)

        await interaction.followup.send(file=discord.File("valorantAccountStats.png"))
        os.remove("valorantAccountStats.png")




    #SECTION: Get user stats from match history. Provide avereage stats, match history stats and other stats (most played agent, etc.)
    async def createStatsImage(self, averageStats:dict, gameStats:dict, otherStats:dict):
        imagesRequired = math.ceil(len(gameStats)/5)
        #print("images required:", imagesRequired)
        for image in range(imagesRequired):
            img = Image.new('RGB', (1200, 1400), color = (6, 9, 23))
            draw = ImageDraw.Draw(img, "RGBA")

            fnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=45)
            userfnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=30)
            boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=50)

            #print("most played agent again:", otherStats["mostPlayedAgent"])

            #Draw average stats and most played agent
            urllib.request.urlretrieve(otherStats["mostPlayedAgent"]["agentPfp"], "mostPlayedAgent.png")
            mostPlayedAgent = Image.open("mostPlayedAgent.png")
            
            mostPlayedAgent = mostPlayedAgent.resize([200,200])
            img.paste(mostPlayedAgent, (0,0))
            os.remove("mostPlayedAgent.png")
            for i in range(len(averageStats)):
                draw.text([(210+i*200),0], f"{list(averageStats.keys())[i]}", font=boldfnt, fill=(255,255,255))
                draw.text([(210+i*200), 100], f"{list(averageStats.values())[i]}", font=fnt, fill=(255,255,255))
            #Draw the line dividing average stats and match history
            draw.line([(0,200),(img.width, 200)], fill=(256,256,256), width=15)

            #Draw the match history
            draw.text((210, 200), "Match", font=boldfnt, fill=(255,255,255))
            draw.text((410, 200), "ACS", font=boldfnt, fill=(255,255,255))
            draw.text((610, 200), "ADR", font=boldfnt, fill=(255,255,255))
            draw.text((810, 200), "HS%", font=boldfnt, fill=(255,255,255))
            draw.text((1010,200), "DD", font=boldfnt, fill=(255,255,255))

            for i in range(0+(image*5),5+(image*5)):
                try:
                    game = gameStats[i]
                except IndexError:
                    break
                #print(f"{i}: {str(game)}")
                urllib.request.urlretrieve(game["agentPfp"], f"agentPfp{i}.png")
                j=i
                if i > 4:
                    j = i - (image*5)
                
                scoreline = game["matchDetails"]["playerSidedScore"]
                scoreline = scoreline.split(" - ")
                if int(scoreline[0])> int(scoreline[1]):
                    win = True
                elif int(scoreline[0]) < int(scoreline[1]):
                    win = False
                else:
                    agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(125, 120, 24))

                agentPfp = Image.open(f"agentPfp{i}.png")
                if win:
                    agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(3, 54, 8))
                elif win == False:
                    agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(43, 2, 6))
                else:
                    agentPfpBckg = Image.new("RGBA", agentPfp.size, color=(125, 120, 24))
                agentPfpBckg.paste(agentPfp, (0,0), mask = agentPfp)
                os.remove(f"agentPfp{i}.png")
                agentPfpBckg.convert("RGB").save(f"agentPfp{i}.jpg")
                agentPfp = Image.open(f"agentPfp{i}.jpg")
                agentPfp = agentPfp.resize([200,200])
                img.paste(agentPfp, (0, 320+(j*200)))

                if win:
                    draw.rectangle([(0, 320+(j*200)), ((2, 520+(j*200)))], fill=(0,255,0))
                    draw.rounded_rectangle([(200, 320+(j*200)), ((img.width, 520+(j*200)))], fill=(0,255,0,40), radius= 2)
                else:
                    draw.rectangle([(0, 320+(j*200)), ((2, 520+(j*200)))], fill=(255,0,0))
                    draw.rounded_rectangle([(200, 320+(j*200)), ((img.width, 520+(j*200)))], fill=(255,0,0,40), radius= 2)
                os.remove(f"agentPfp{i}.jpg")

                draw.text((210, 320+(j*200)), f"{game['matchDetails']['map']}\n{game['matchDetails']['playerSidedScore']}", font=fnt, fill=(255,255,255))
                draw.text((210, 430+(j*200)), f"{game['KDA']}\n{str(game['matchDetails']['mode'])}", font=userfnt, fill=(255,255,255))
                draw.text((410, 320+(j*200)), f"{game['ACS']}", font=fnt, fill=(255,255,255))
                draw.text((610, 320+(j*200)), f"{game['ADR']}", font=fnt, fill=(255,255,255))
                draw.text((810, 320+(j*200)), f"{game['HS']}", font=fnt, fill=(255,255,255))
                draw.text((1010,320+(j*200)), f"{game['DD']}", font=fnt, fill=(255,255,255))
            print("saving userCollectedStats")
            img.save(f"userCollectedStats{image}.png")
    
    async def calculateUserStatsFromGames(self, response, user): # Returns [matchStats, averagedStats, gameStats, otherStats] or an error
        gameStats = [] # specific player stats of a game. contains all the game stats in the format of {"matchDetails": {"map": map, "playerSidedScore": "Red - Blue", "mode": mode}, "kills": kills, "deaths": deaths, "assists": assists, "KDA": "kills/deaths/assists", "KDR": kills/deaths, "ACS": ACS, "ADR": ADR, "DD": DD, "rank": rank, "team": team, "HS": HS, "agentPfp": agentPfp}
        averagedStats = {"ADR": 0, "ACS": 0, "KDR": 0, "HS": 0}

        mostPlayedAgent = {}
        mostPlayedAgentArr = [] # used for containing mostPlayedAgentFormatting {agent name: {timesPlayed: count, agentPfp: url}}

        matchStats = []
        otherStats = {
            "mostPlayedAgent": None,
            "winrate": {"wins": 0, "losses": 0, "draws": 0}
        }

        # function for sorting mostPlayedAgent
        def sortLowestToHighest(arr:list):
            length = len(arr)
            print(arr)
            try:
                for i in arr:
                    for j in arr:
                        iagentName = list(i.keys())[0]
                        jagentName = list(j.keys())[0]

                        print(f"{iagentName}:{i[iagentName]['timesPlayed']}, {jagentName}:{j[jagentName]['timesPlayed']}")
                        if i[iagentName]['timesPlayed'] > j[jagentName]['timesPlayed']:
                            arr[arr.index(i)], arr[arr.index(j)] = arr[arr.index(j)], arr[arr.index(i)]
                
                return arr[0][list(arr[0].keys())[0]] # returns most played agent's {agentName:{timesPlayed: count, agentPfp: url}}
            except IndexError:
                return None

        for l in range(len(response["data"])):
            i = response["data"][l]
            matchDetails = i["metadata"]
            playerDetails = i["players"]["all_players"]
            for k in playerDetails:
                if k["puuid"] == user["data"]["puuid"]:
                    requestedUser = k
            
            teamDetails = i["teams"]
            #print(str(matchDetails) + "\n\n", str(requestedUser) + "\n\n", str(teamDetails) + "\n\n---")

            try:
                totalRoundsPlayed = teamDetails["red"]["rounds_won"] + teamDetails["blue"]["rounds_won"]
            except TypeError:
                continue

            if matchDetails["mode_id"] not in ["competitive", "unrated", "premier"]:
                continue
            
            gameStats.append({
                "matchDetails": {"map": matchDetails["map"], "playerSidedScore": f"{teamDetails[str(requestedUser['team']).lower()]['rounds_won']} - {teamDetails[str(requestedUser['team']).lower()]['rounds_lost']}", "mode": matchDetails["mode_id"]},
                "kills": requestedUser["stats"]["kills"], #int
                "deaths": requestedUser["stats"]["deaths"], #int
                "assists": requestedUser["stats"]["assists"], #int
                "KDA": f'{requestedUser["stats"]["kills"]}/{requestedUser["stats"]["deaths"]}/{requestedUser["stats"]["assists"]}', #string
                "KDR": requestedUser["stats"]["kills"]/requestedUser["stats"]["deaths"], #float
                "ACS": round((requestedUser["stats"]["score"]/totalRoundsPlayed), 2), #float
                "ADR": round((requestedUser["damage_made"]/totalRoundsPlayed),2), #float
                "DD": math.floor((requestedUser["damage_made"]/totalRoundsPlayed)-(requestedUser["damage_received"]/totalRoundsPlayed)), #float -> int
                "rank": requestedUser["currenttier_patched"], #string
                "team": requestedUser["team"], #string
                "HS": f'{round((requestedUser["stats"]["headshots"]/(requestedUser["stats"]["bodyshots"]+requestedUser["stats"]["headshots"]+requestedUser["stats"]["legshots"])*100),2)}%', #string because of % sign
                "agentPfp": requestedUser["assets"]["agent"]["small"] #string
            })
            print(gameStats[l])
            try:
                mostPlayedAgent.update({requestedUser["character"]: {"timesPlayed": mostPlayedAgent[requestedUser["character"]]["timesPlayed"] + 1, "agentPfp": requestedUser["assets"]["agent"]["small"], "agentName": requestedUser["character"]}})
            except KeyError:
                mostPlayedAgent.update({requestedUser["character"]: {"timesPlayed": 1, "agentPfp": requestedUser["assets"]["agent"]["small"], "agentName": requestedUser["character"]}})
            
            if teamDetails[str(requestedUser["team"]).lower()]["rounds_won"] > teamDetails[str(requestedUser["team"]).lower()]["rounds_lost"]:
                otherStats.update({"winrate": {"wins": otherStats["winrate"]["wins"] + 1, "losses": otherStats["winrate"]["losses"], "draws": otherStats["winrate"]["draws"]}})
            elif teamDetails[str(requestedUser["team"]).lower()]["rounds_won"] < teamDetails[str(requestedUser["team"]).lower()]["rounds_lost"]:
                otherStats.update({"winrate": {"wins": otherStats["winrate"]["wins"], "losses": otherStats["winrate"]["losses"] + 1, "draws": otherStats["winrate"]["draws"]}})
            else:
                otherStats.update({"winrate": {"wins": otherStats["winrate"]["wins"], "losses": otherStats["winrate"]["losses"], "draws": otherStats["winrate"]["draws"] + 1}})
            
            matchStats.append([matchDetails, playerDetails, teamDetails])
        
        for i in mostPlayedAgent:
            print("appending", i, mostPlayedAgent[i])
            mostPlayedAgentArr.append({i: mostPlayedAgent[i]}) # appends {agent name: {timesPlayed: count, agentPfp: url}}

        # Sorts the most played agent by the amount of times played. This function returns an array of the most played agents in order of most played to least played.
        mostPlayedAgent = sortLowestToHighest(mostPlayedAgentArr) # returns the most played agent's [{timesPlayed: count}, {agentPfp: url}]
        if mostPlayedAgent == None:
            return "No favourite agent found."
        # Calculate the average stats for all comp, unrated and premier games requested
        for i in range(len(gameStats)):
            specificGameStats = gameStats[i]
            averagedStats["ADR"] += specificGameStats["ADR"]
            averagedStats["ACS"] += specificGameStats["ACS"]
            averagedStats["KDR"] += specificGameStats["KDR"]
            averagedStats["HS"] += float(specificGameStats["HS"].replace("%", ""))

        averagedStats["ADR"] = round(averagedStats["ADR"]/len(gameStats),2)
        averagedStats["ACS"] = round(averagedStats["ACS"]/len(gameStats), 2)
        averagedStats["KDR"] = round(averagedStats["KDR"]/len(gameStats),2)
        averagedStats["HS"] = str(round(averagedStats["HS"]/len(gameStats),2)) + "%"
        
        otherStats["mostPlayedAgent"] = mostPlayedAgent

        return {"matchStats": matchStats, "averagedStats": averagedStats, "gameStats": gameStats, "otherStats": otherStats}



    @app_commands.command(name="get_valorant_stats", description="Get your valorant stats")
    @app_commands.choices(mode=[app_commands.Choice(name="Competitive", value="competitive"), app_commands.Choice(name="Unrated", value="unrated"), app_commands.Choice(name="Premier", value="premier")])
    @app_commands.describe(user = "Grab user's match history.", amount = "Amount of games to get. Max is 10.", mode = "Mode of the games to get.")
    async def getGames(self, interaction:discord.Interaction, user:discord.Member=None, amount:int=5, mode:app_commands.Choice[str]=None):
        await interaction.response.defer()
        message = await interaction.original_response()

        if amount > 10 or amount < 1:
            return await interaction.followup.send("Amount of games cannot exceed 10 or be under 1", ephemeral=True)
        URL = "https://api.henrikdev.xyz"
        userAccount = {}

        if os.path.exists("riotdetails.json"):
            with open("riotdetails.json", "r") as file:
                    try:
                        riotDetails = json.load(file)
                        if user == None:
                            userAccount = riotDetails[str(interaction.user.id)]
                        else:
                            userAccount = riotDetails[str(user.id)]
                    except:
                        return await interaction.followup.send("User has not logged in yet! They must run /login_for_valorant before trying this command", ephemeral=True)
        else:
            return await interaction.followup.send("Run /login_for_valorant before running this command!", ephemeral=True)

        logger.info(f"Getting games for {userAccount['data']['name']}")        
        region = userAccount['data']['region']
        if mode == None:
            response = requests.get(url=f"{URL}/valorant/v3/by-puuid/matches/{region}/{userAccount['data']['puuid']}?size={amount}")
        else:
            response = requests.get(url=f"{URL}/valorant/v3/by-puuid/matches/{region}/{userAccount['data']['puuid']}?mode={mode.value}&size={amount}")
        response = response.json()


        if(response["status"] != 200):
            logger.info(response)
            return await interaction.followup.send(f"Error with the status of {response['status']}", ephemeral=True)
        
        try:
            userStatsOverMatchHistory = await self.calculateUserStatsFromGames(response, userAccount) # returns {"matchStats": matchStats, averagedStats, gameStats, otherStats
            allGamesData = userStatsOverMatchHistory["matchStats"]
            averagedStats = userStatsOverMatchHistory["averagedStats"]
            otherStats = userStatsOverMatchHistory["otherStats"]
            gameStats = userStatsOverMatchHistory["gameStats"]
        except TypeError:
            return await interaction.followup.send("Failure! Stats are unfetchable.", ephemeral=True)

        await self.createStatsImage(averagedStats, gameStats, otherStats)

        imagesRequired = math.ceil(amount/5)

        matchHistoryUI = selectMatchUI()

        for i in range(imagesRequired):
            try:
                matchHistoryUI.timeout = 600
                matchHistorySelect:discord.ui.Select = matchHistoryUI.children[0]
                matchHistorySelect.options.clear()
                
                for k in range(len(allGamesData)):
                    IndividualMatchData = allGamesData[k]
                    matchHistorySelect.add_option(label=f"Match {k+1}", value=f"{k+1}")
                valorant.matchStats = allGamesData
                valorant.userAccount = userAccount
                await interaction.followup.send(file=discord.File(f"userCollectedStats{i}.png", f"userCollectedStats{i}.png"), view=matchHistoryUI)
                os.remove(f"userCollectedStats{i}.png")
                
            except FileNotFoundError:
                break


    #SECTION: Create stat images from match data
    # Function for formatting images from match data. Use this to create the images for the match data, not the other functions.
    def formatMatchEmbed(messageid, response=None, puuid=None):       

        finalGameStats = {}
        print(type(response))
        #assigns details from response JSON file acquired from match only if it's a response directly from the API.
        if type(response) == dict:
            matchDetails = response["data"][0]["metadata"]
            playerDetails = response["data"][0]["players"]["all_players"]
            teamDetails = response["data"][0]["teams"]
        elif response != None:
            matchDetails = response[0]
            playerDetails = response[1]
            teamDetails = response[2]
        
            # for i in range(len(response)):
            #     print(i)
            #     with open ("matchdetails.json", "a+") as file:
            #         json.dump(response[i], file, indent=4)

            with open("matchdetails.json", "w") as file:
                json.dump(response[0], file, indent=4)

        
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
        
        #print(json.dumps(finalGameStats, indent=4))
        personalUserStats = finalGameStats[requestedUser["name"]]

        valorant.createUserStatsImage(matchDetails["map"], personalUserStats["agentPfp"], personalUserStats, {"Red": teamDetails["red"]["rounds_won"], "Blue": teamDetails["blue"]["rounds_won"]}, messageid,username=requestedUser["name"])
        valorant.createTotalGameStatsImage(matchDetails["map"], finalGameStats, {"Red": teamDetails["red"]["rounds_won"], "Blue": teamDetails["blue"]["rounds_won"]}, messageid)
    
    # Function for creating the image for all players in a match data.
    def createTotalGameStatsImage(map:str, stats:dict, score:dict, messageId):
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

        ranks = {
            "Iron 1": "images/valorantRanks/Iron_1_Rank.png",
            "Iron 2": "images/valorantRanks/Iron_2_Rank.png",
            "Iron 3": "images/valorantRanks/Iron_3_Rank.png",
            "Bronze 1": "images/valorantRanks/Bronze_1_Rank.png",
            "Bronze 2": "images/valorantRanks/Bronze_2_Rank.png",
            "Bronze 3": "images/valorantRanks/Bronze_3_Rank.png",
            "Silver 1": "images/valorantRanks/Silver_1_Rank.png",
            "Silver 2": "images/valorantRanks/Silver_2_Rank.png",
            "Silver 3": "images/valorantRanks/Silver_3_Rank.png",
            "Gold 1": "images/valorantRanks/Gold_1_Rank.png",
            "Gold 2": "images/valorantRanks/Gold_2_Rank.png",
            "Gold 3": "images/valorantRanks/Gold_3_Rank.png",
            "Platinum 1": "images/valorantRanks/Platinum_1_Rank.png",
            "Platinum 2": "images/valorantRanks/Platinum_2_Rank.png",
            "Platinum 3": "images/valorantRanks/Platinum_3_Rank.png",
            "Diamond 1": "images/valorantRanks/Diamond_1_Rank.png",
            "Diamond 2": "images/valorantRanks/Diamond_2_Rank.png",
            "Diamond 3": "images/valorantRanks/Diamond_3_Rank.png",
            "Immortal 1": "images/valorantRanks/Immortal_1_Rank.png",
            "Immortal 2": "images/valorantRanks/Immortal_2_Rank.png",
            "Immortal 3": "images/valorantRanks/Immortal_3_Rank.png",
            "Radiant": "images/valorantRanks/Radiant_Rank.png"
        }

        scoreLine = f"{score['Blue']} - {score['Red']}"
        mapLink = mapLoadScreens[map]
        urllib.request.urlretrieve(mapLink, "map.png")

        img = Image.new('RGB', (800, 1200), color = (6, 9, 23))
        draw = ImageDraw.Draw(img)

        fnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=17)
        boldfnt = ImageFont.truetype(font="fonts/OpenSans-Bold.ttf", size=80)

        def sortLowestToHighest(arr, stat):
            length = len(arr)

            for i in range(length):
                for j in range(0, length):
                    #print(str(i), str(j))
                    #print(f"i: {str(arr[i])} {str(stats[arr[i]]['ACS'])}, j: {str(arr[j])} {str(stats[arr[j]]['ACS'])}")
                    
                    if stats[arr[i]][stat] > stats[arr[j]][stat]:
                        #print(f"Swapping {arr[i]} with {arr[j]}")
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
        mapImage = mapImage.resize([800, 454])
        mapImage = ImageChops.offset(mapImage, mapImage.width, math.floor((mapImage.height)/2))
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
            draw.text((105, 170+(i*100)), f"{name}: #{stats[blue_team[i]]['tag']}", font=fnt, fill=(255,255,255))

            #draw rank
            if(stats[blue_team[i]]["rank"]) != "Unrated":
                rankImage = Image.open(ranks[stats[blue_team[i]]["rank"]])
                rankImage = rankImage.resize([50, 50])
                img.paste(rankImage, (105, 195+(i*100)))
            #draw.text((105, 190+(i*100)), f"{stats[blue_team[i]]['rank']}", font=fnt, fill=(255,255,255))

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
            if(stats[red_team[i]]["rank"]) != "Unrated":
                rankImage = Image.open(ranks[stats[red_team[i]]["rank"]])
                rankImage = rankImage.resize([45, 45])
                img.paste(rankImage, (105, 695+(i*100)))

            #draw.text((105, 690+(i*100)), f"{stats[red_team[i]]['rank']}", font=fnt, fill=(255,255,255))

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
        for i in range(totalPlayerCount+1):
            try:
                os.remove(f"agentPfp{i}.png")
            except:
                continue


    # Personal stats in a single match. Parameters are the map name, the agent picture link, user stats and the score in the format of {"Red": 0, "Blue": 0}
    def createUserStatsImage(map:str, agentPfp:str, userStats:dict, score:dict, messageId, username):
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
        userfnt = ImageFont.truetype(font="fonts/OpenSans-Regular.ttf", size=15)
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
        agentProfilePictureBckg = Image.new("RGBA", agentProfilePicture.size, color=(6, 9, 23))       
        agentProfilePictureBckg.paste(agentProfilePicture, (0,0), mask=agentProfilePicture)
        agentProfilePictureBckg.convert("RGB").save("fixedAgentPfp.jpg")
        agentProfilePicture = Image.open("fixedAgentPfp.jpg")
        agentProfilePicture = agentProfilePicture.resize([190,190])
        img.paste(agentProfilePicture, (0,108))

        #Place player stats on the right of the agent picture
        draw.rectangle([(agentProfilePicture.width + 20, img.width), (666, img.width)],fill=(0,0,0), outline=(33, 38, 46))
        #Username
        draw.text((agentProfilePicture.width + 20, 100), f"{username}", fill=(255,255,255), font=userfnt)
        #Scoreline
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
        os.remove("fixedAgentPfp.jpg")
        
    
    #SECTION: GET LATEST GAMES
    @app_commands.command(name="get_latest_comp_game", description="Get your recent game stats")
    @app_commands.describe(user = "Grab user's latest game. Optional.")
    async def getRecentGame(self, interaction: discord.Interaction, user:discord.Member=None):
        await interaction.response.defer()
        message = await interaction.original_response()
        URL = "https://api.henrikdev.xyz"
        userAccount = {}

        if os.path.exists("riotdetails.json"):
            with open("riotdetails.json", "r") as file:
                    try:
                        riotDetails = json.load(file)
                        if user == None:
                            userAccount = riotDetails[str(interaction.user.id)]
                        else:
                            userAccount = riotDetails[str(user.id)]
                    except:
                        return await interaction.followup.send("User has not logged in yet! They must run /login_for_valorant before trying this command", ephemeral=True)
        else:
            return await interaction.followup.send("Run /login_for_valorant before running this command!", ephemeral=True)

        fetchParameters = {
            "affinity": "ap",
            "puuid": userAccount["data"]["puuid"],
            "mode": "competitive",
            "size": 1
        }
        region = userAccount["data"]["region"]
        response = requests.get(url=f"{URL}/valorant/v3/by-puuid/matches/{region}/{fetchParameters['puuid']}?mode={fetchParameters['mode']}&size={fetchParameters['size']}")
        response = response.json()

        if(response["status"] != 200):
            return await interaction.response.send_message(f"Error with the status of {response['status']}", ephemeral=True)

        valorant.formatMatchEmbed(message.id,response,userAccount["data"]["puuid"])
        
        userStatsFile = discord.File(f"userStats{message.id}.png", filename=f"userStats{message.id}.png")
        gameStatsFile = discord.File(f"gameStats{message.id}.png", filename=f"gameStats{message.id}.png")
        
        await interaction.followup.send(file=userStatsFile, view=matchStatsUI())
        
        await message.edit(delete_after=600)
        message = message.id

        with open("recentGames.txt", "a+") as file:
            file.write(f" {message},")

    async def refreshLoginForValorantDetails(self, interactionId:str): # Returns either an error string or the user's details as well as updating in the json file
        if not os.path.exists("riotdetails.json"):
            return "User has not logged in yet! They must run /login_for_valorant before trying this command"
    
        with open("riotdetails.json", "r") as file:
            riotDetails:dict = json.load(file)
            if str(interactionId) not in riotDetails:
                return "User has not logged in yet! They must run /login_for_valorant before trying this command"
            else:
                userAccount = riotDetails[str(interactionId)]
        
            response = requests.get(url=f"https://api.henrikdev.xyz/valorant/v1/account/{userAccount['data']['name']}/{userAccount['data']['tag']}")
            response.json()

            if(response["status"] != 200):
                return f"Error with the status of {response['status']}"

            riotDetails.update({str(interactionId): response})

            with open("riotdetails.json", "w") as writeFile:
                json.dump(riotDetails, writeFile)
                return riotDetails[str(interactionId)]
    
    async def loginForValorant(self, interactionId:str, username:str, tag:str): # This function logs in user by assinging riot account details with their discord id
        if(username == None):
            with open("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.pop(str(interactionId))
                with open("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)
            
            return f"Deleting {interactionId}'s details"
        
        
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
            return f"Invalid Riot ID or Tag with the error of {response['status']}"

        riotDetails = {}
        try:
        #opens the file and reads the json
            with open ("riotdetails.json", "r") as file:
                riotDetails = json.load(file)
                riotDetails.update({str(interactionId): response})
                with open ("riotdetails.json", "w") as file:
                    json.dump(riotDetails, file)
                    
            return "Updated details!"
        except Exception as e:
            with open ("riotdetails.json", "w+") as file:
                riotDetails.update({str(interactionId): response})
                json.dump(riotDetails, file)
        
            return "Updated details!"
        
    @app_commands.command(name="login_for_valorant", description="Login into your account")
    @app_commands.describe(username = "Enter your Valorant username. If you leave it empty, it will delete your information.")
    async def loginValorant(self, interaction:discord.Interaction, username:str, tag:str):
        await interaction.response.defer()
        response = await self.loginForValorant(interaction.user.id, username, tag)
        await interaction.followup.send(response, ephemeral=True)

    @app_commands.command(name="dev_valorant_clear", description="Clears the recent games list and any images that wasn't deleted")
    async def clearRecentGames(self, interaction:discord.Interaction):
        if str(interaction.user.id) not in settings.DEV:
            return await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)

        with open("recentGames.txt", "w") as file:
            file.write("")

        for i in os.listdir(os.getcwd()):
            if "userStats" in i or "gameStats" in i:
                os.remove(i)

        await interaction.response.send_message("Cleared recent games list and images", ephemeral=True)

    #SECTION: PREMIER TEAMS
    def formatTeamInfo(self, information):
        description = [f"**Name:** {information['name']}#{information['tag']}",
                       f"**Win/loss:** {information['wins']}/{information['losses']}",
                       f"**Score:** {information['score']}/675",
                       f"**Standings:** {information['ranking']}"
                       ]
        
        description = "\n".join(description)
        embed = discord.Embed(title=f"{information['name']}", description=description)
        embed.set_thumbnail(url=information["customization"]["image"])
        embed = embed.set_footer(text="This a work in progress embed. Currently, the API's premier function is not working, so this is the workaround for now.")

        return embed

    @app_commands.command(name="gcgs_premier", description="Get information on the Generic Cursed Valorant team!")
    async def getGCGSVAL(self, interaction:discord.Interaction):
        if str(interaction.user.id) not in settings.DEV:
            return await interaction.response.send_message("This command is a work in progress!", ephemeral=True)
        
        await interaction.response.defer()
        team = {}

        response = requests.get(url="https://api.henrikdev.xyz/valorant/v1/premier/search?name=GCGSval&tag=GCVT")
        response = response.json()

        if(response["status"] != 200):
            return await interaction.followup.send(f"Error with the status of {response['status']}", ephemeral=True)
        
        for i in response["data"]:
            if i["name"] == "GCGSval":
                team = i

        embed = self.formatTeamInfo(team)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="get_premier_team", description="Get information on a premier team")
    @app_commands.describe(team_name = "The team you want to get information on", tag = "The tag of the team")
    async def getPremierTeam(self, interaction:discord.Interaction, team_name:str, tag:str=None):
        await interaction.response.defer()
        team = {}
        if tag != None:
            response = requests.get(url=f"https://api.henrikdev.xyz/valorant/v1/premier/search?name={team_name}")
        else:
            response = requests.get(url=f"https://api.henrikdev.xyz/valorant/v1/premier/search?name={team_name}&tag={tag}")

        response = response.json()

        if(response["status"] != 200):
            return await interaction.followup.send(f"Error with the status of {response['status']}", ephemeral=True)
        

        print(json.dumps(response, indent=4))
        for i in response["data"]:
            try:
                if str(i["name"]).lower() == team_name.lower():
                    team = i
            except:
                continue
        
        if team != {}:
            embed = self.formatTeamInfo(team)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"{team_name} not found")

async def setup(bot):
    await bot.add_cog(valorant(bot, None, None))