import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import sys

import json
import requests

import csv
from zipfile import ZipFile

from math import floor

from dateutil import tz
from datetime import datetime, time

from bs4 import BeautifulSoup

date = datetime.now(tz=tz.tzlocal())
midnight = time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz.tzlocal())
letterboxdLogo = "https://a.ltrbxd.com/logos/letterboxd-decal-dots-pos-rgb-500px.png"

letterboxdDetails = {
    "chat": "",
    "users": {},
    "films": {}
}
letterboxdURL = os.getenv("LETTERBOXD_URL")

import settings 
logger = settings.logging.getLogger("bot")

class letterboxd(commands.Cog):
    def __init__(self, bot:discord.Client):
        self.bot = bot
        self.letterboxdDetails = letterboxdDetails

        if os.path.exists("letterboxd.json"):
            with open("letterboxd.json", "r") as f:
                self.letterboxdDetails = json.load(f)
        
        self.getLetterboxd.start()

    def fetchFromTMDBid(self, tmdbId:int):
        pass

    def getActivityCount(self, user:discord.Member, data:dict) -> int:
        try:
            count = self.letterboxdDetails["users"][str(user.id)]["activity"].index(data)
            print(f"activity count:", count)
        except:
            count = -1
        return count

    async def fetchFromLetterboxd(self, user:discord.Member = None, letterboxdUser=None, amount=1, patron:bool=False) -> list:
        """
        Fetches ``amount`` of films for a ``user``'s discord id or ``letterboxdUser`` username
        """


        if user != None:
            if self.letterboxdDetails['users'][str(user.id)]["patron"] == None:
                self.letterboxdDetails['users'][str(user.id)]["patron"] = False
            try:
                user = self.letterboxdDetails["users"][str(user.id)]["username"]
                url = f"{letterboxdURL}/{user}?amount={amount}&patron={int(self.letterboxdDetails['users'][str(user.id)]['patron'])}"
            except KeyError:
                return None
        elif letterboxdUser != None:
            url = f"{letterboxdURL}/{letterboxdUser}?amount={amount}&patron={int(patron)}"
        else:
            raise ValueError("Either a user or a letterboxd username must be provided")
            return None
        
        print(f"fetching from {url}")
        
        response = requests.get(url=url)
        response = response.json()

        return response["films"]
    
    async def fetchMemberFromId(self, userID:int) -> discord.Member:
        user = await self.bot.fetch_user(userID)
        return user

    def createReviewEmbed(self, data:dict, user, interaction:discord.Interaction=None):
        """
        Returns a ``discord.Embed`` object using the data acquired from the API.
        """
        print("\ncreating review embed with", data)
        if type(user) != discord.Member and type(user) != discord.User:
            user = self.fetchMemberFromId(int(user)) # Fetches user object from discord id

        if data["film"]["title"] in self.letterboxdDetails["films"].keys():
            self.letterboxdDetails["films"][data["film"]["title"]].update({str(user.id): data})
        else:
            self.letterboxdDetails["films"][data["film"]["title"]] = {str(user.id): data}

        with open("letterboxd.json", "w") as f:
                json.dump(self.letterboxdDetails, f, indent=4)

        if interaction != None:
            return letterboxdFilmEmbed(data=data, author=user, letterboxd=self), letterboxdFilmWatchUI(self, user, self.getActivityCount(user, data), interaction)
        return letterboxdFilmEmbed(data=data, author=user, letterboxd=self), None

   
    @app_commands.command(name="letterboxd_setup", description="Set up the Letterboxd channel for the bot to post in")
    async def letterboxdSetup(self, interaction:discord.Interaction, chat:discord.TextChannel):
        for role in interaction.user.roles:
            print(role.permissions.manage_channels)
            if role.permissions.manage_channels or role.permissions.administrator:
                break
        else:
            return await interaction.response.send_message("You do not have the required permissions to run this command", ephemeral=True)
        
        with open("letterboxd.json", "w") as f:
            self.letterboxdDetails["chat"] = chat.id
            json.dump(self.letterboxdDetails, f, indent=4)
        return await interaction.response.send_message(f"Letterboxd channel has been set to {chat.mention}", ephemeral=True)
    
    @app_commands.command(name="letterboxd_patron", description="Enable or disable Letterboxd Patron features if you are a patron.")
    async def letterboxdPatron(self, interaction:discord.Interaction):
        user = interaction.user
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("You have not signed in for Letterboxd tracking", ephemeral=True)

        if self.letterboxdDetails["users"][str(user.id)]["patron"]:
            self.letterboxdDetails["users"][str(user.id)]["patron"] = False
            await interaction.response.send_message("You have disabled Letterboxd Patron features.", ephemeral=True)
        else:
            self.letterboxdDetails["users"][str(user.id)]["patron"] = True
            await interaction.response.send_message("You have enabled Letterboxd Patron features.", ephemeral=True)

        with open("letterboxd.json", "w") as f:
            json.dump(self.letterboxdDetails, f, indent=4)
        
    @app_commands.command(name="letterboxd_login", description="Opt in for Letterboxd tracking. Run this command again to opt out.")
    @app_commands.describe(letterboxdusername= "Your Letterboxd username or your Letterboxd profile URL")
    async def letterboxdLogin(self, interaction:discord.Interaction, letterboxdusername:str, patron:bool=False):
        await interaction.response.defer()
        if str(interaction.user.id) in self.letterboxdDetails["users"]:
            self.letterboxdDetails["users"].pop(str(interaction.user.id))

            with open("letterboxd.json", "w") as f:
                json.dump(self.letterboxdDetails, f, indent=4)

            return await interaction.followup.send("You have opted out of Letterboxd tracking.", ephemeral=True)
        else:
            if "letterboxd.com" in letterboxdusername:
                letterboxdusername = letterboxdusername.split(".com/")[1].rstrip("/")

            try:
                response = await self.fetchFromLetterboxd(letterboxdUser=letterboxdusername, amount=5)
            except Exception as e:
                logger.error(f"Error fetching data for {letterboxdusername}: {e}")
                return await interaction.followup.send("There was an error fetching data. Please try again some other time.", ephemeral=True)
                
            
            self.letterboxdDetails["users"][str(interaction.user.id)] = {
                "username": letterboxdusername,
                "patron": patron,
                "discord username": interaction.user.display_name,
                "activity": response,
                "favourites": []
            }
            
            with open("letterboxd.json", "w") as f:
                json.dump(self.letterboxdDetails, f, indent=4)

            return await interaction.followup.send("You have opted in for Letterboxd tracking.", ephemeral=True)

    #@app_commands.command(name="fetch_favourites", description="Fetch the user's favourite films")
    async def fetchFavourites(self, interaction:discord.Interaction, user:discord.Member=None):
        if user == None:
            user = interaction.user

        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("The user is not signed in for Letterboxd tracking", ephemeral=True)

        response = self.letterboxdDetails["users"][str(user.id)]["favourites"]
        if response == None:
            return await interaction.response.send_message("There was an error fetching data. Has the user logged in with /letterboxd_login?", ephemeral=True)
        
        response = requests.get(url=f"letterboxd.com/{user}")
        response = BeautifulSoup(response.content, "html.parser")
        
        favourites = []
        for film in response.find_all("li", attrs={"data-object-name": "favorite film"}):
            filmName = film.find("div", {"data-film-name": True})["data-film-name"]
            
            filmLink = film.find("a", {"href": True})["href"]
            filmLink = f"https://letterboxd.com{filmLink}"

            response = requests.get(filmLink)
            response = BeautifulSoup(response.content, "html.parser")
            
            tmdbID = response.find("body", {"data-tmdb-id": True})["data-tmdb-id"]
            response = requests.get(f"{letterboxdURL}/film/{tmdbID}")
            response = response.json()

        interaction.response.send_message("Favourites have been fetched!", ephemeral=True)


    @app_commands.command(name="letterboxd_upload_profile", description="Upload profile data exported from Letterboxd.")
    async def uploadProfileData(self, interaction:discord.Interaction, attachment:discord.Attachment):
        await interaction.response.defer()
        if attachment.content_type == "zip":
            with ZipFile(attachment.filename, 'r') as zip:
                zip.extractall()
            
            for file in os.listdir():
                if ".csv" in file:
                    
                    with open(file) as csvFile:
                        csvFile = csv.reader(file, delimiter=' ')
        else:
            return interaction.response.send_message("Error parsing attachment, please try again later.", ephemeral=True)
        pass

    @app_commands.command(name="letterboxd_fetch_last", description="Fetch the latest Letterboxd activity")
    async def fetchLatestLetterBoxd(self, interaction:discord.Interaction, user:discord.Member=None):
        if user == None:
            user = interaction.user
            
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("You have not signed in for Letterboxd tracking", ephemeral=True)

        response = self.letterboxdDetails["users"][str(user.id)]["activity"]
        if response == None:
            return await interaction.response.send_message("There was an error fetching data. Has the user logged in with /letterboxd_login?", ephemeral=True)
        
        embed, ui = self.createReviewEmbed(data=response[0], user=user, interaction=interaction)
        await interaction.response.send_message(embed=embed, view=ui)

    @app_commands.command(name="fetch_letterboxd_activity", description="Fetch the latest Letterboxd activity")
    async def fetchLetterBoxdActivity(self, interaction:discord.Interaction, user:discord.Member=None):
        if user == None:
            user = interaction.user
            
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("User have not signed in for Letterboxd tracking", ephemeral=True)
        
        response = self.letterboxdDetails["users"][str(user.id)]["activity"]
        embed = letterboxdActivityEmbed(activity=response, user=user, letterboxd=self)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="update_letterboxd_activity", description="Fetch the latest Letterboxd activity")
    async def updateLetterBoxdActivity(self, interaction:discord.Interaction):
        user = interaction.user
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("User have not signed in for Letterboxd tracking", ephemeral=True)
        
        response = await self.fetchFromLetterboxd(user=user, amount=5)
        if response == None:
            return await interaction.response.send_message("There was an error fetching data. Has the user logged in with /letterboxd_login?", ephemeral=True)
        
        self.letterboxdDetails["users"][str(user.id)]["activity"] = response
        with open("letterboxd.json", "w") as f:
            json.dump(self.letterboxdDetails, f, indent=4)

        await interaction.response.send_message("Activity has been updated!", ephemeral=True)
        
    @tasks.loop(hours=1)
    async def getLetterboxd(self):
        for user in self.letterboxdDetails["users"]:
            print(f"checking for activity from {user}")
            username = self.letterboxdDetails["users"][user]["username"]
            try:
                self.letterboxdDetails["users"][user]["patron"] == None
            except KeyError:
                self.letterboxdDetails["users"][user]["patron"] = False
            patron = self.letterboxdDetails["users"][user]["patron"]

            try:
                discordUsername = self.bot.get_user(int(user)).display_name
            except:
                discordUsername = None
        
            self.letterboxdDetails["users"][user].update({"discord username": discordUsername})

            response = await self.fetchFromLetterboxd(letterboxdUser=username, amount=5, patron=patron)
            if response == None:
                return logger.error(f"Error fetching data for {user}")

            for filmCount in range(len(response)):
                print(f"\nchecking if {response[filmCount]} is in {user}'s activity")

                memberReviews = []
                for activity in self.letterboxdDetails["users"][user]["activity"]:
                    memberReviews.append(activity["member"])

                if not (response[filmCount]["member"] in memberReviews):
                    print("Not in activity, sending message\n")
                    member = await self.bot.fetch_user(user)
                    try:
                        embed, ui = self.createReviewEmbed(data=response[filmCount], user=member)
                        channel = self.bot.get_channel(int(self.letterboxdDetails["chat"]))
                        await channel.send(embed=embed, view=ui)
                    except Exception as e:
                        raise e
                    

                    self.letterboxdDetails["users"][user]["activity"].insert(filmCount, response[filmCount])
                    if len(self.letterboxdDetails["users"][user]["activity"]) > 5:
                        self.letterboxdDetails["users"][user]["activity"].pop(5)

        with open("letterboxd.json", "w") as f:
            json.dump(self.letterboxdDetails, f, indent=4)

    # WIP @tasks.loop(time=midnight)
    async def getLast5(self):
        if date.weekday() == 4:
            for user in self.letterboxdDetails["users"]:
                response = requests.get(url=letterboxdURL)
                response = response.json()
        
    def checkIfSignedIn(self, user:discord.Member) -> bool:
        """
        Checks if a user of type ``discord.Member`` is signed in for Letterboxd tracking.
        """
        print(f"checking for {str(user.id)} in {list(self.letterboxdDetails['users'].keys())}")
        keys = list(self.letterboxdDetails["users"].keys())
        if str(user.id) in keys:
            return True
        else:
            return False
        
    def ratingEmojis(self, rating) -> str:
        rating = float(rating)
        if rating.is_integer():
            return "⭐" * floor(rating)
        else:
            return ("⭐" * floor(rating)) + "½"
        
# UI Elements
class letterboxdFilmWatchUI(discord.ui.View):
    def __init__(self, letterboxd:letterboxd, user:discord.Member, count:int, interaction:discord.Interaction=None):
        super().__init__()
        self.letterboxd = letterboxd
        self.user:discord.Member = user
        self.count = count
        self.interaction:discord.Interaction = interaction

        userActivity = self.letterboxd.letterboxdDetails["users"][str(user.id)]["activity"]
        if self.count == -1:
            self.previous.disabled = True
            self.next.disabled = True
        if self.count + 1 == len(userActivity):
            self.next.disabled = True
        if self.count - 1 == -1:
            self.previous.disabled = True
        
        self.film = userActivity[self.count]
        self.reviews = self.letterboxd.letterboxdDetails["films"][self.film["film"]["title"]]

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction:discord.Interaction, button:discord.ui.Button, ):
        userID = str(self.user.id)
        previousFilm = self.letterboxd.letterboxdDetails["users"][userID]["activity"][self.count - 1]
        embed, ui = self.letterboxd.createReviewEmbed(data=previousFilm, user=self.user, interaction=self.interaction)
        await interaction.response.edit_message(embed=embed, view=ui)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction:discord.Interaction, button:discord.ui.Button, ):
        print(f"fetching next film in {self.user.display_name}'s activity")
        userID = str(self.user.id)
        nextFilm = self.letterboxd.letterboxdDetails["users"][userID]["activity"][self.count + 1]
        embed, ui = self.letterboxd.createReviewEmbed(data=nextFilm, user=self.user, interaction=self.interaction)
        await interaction.response.edit_message(embed=embed, view=ui)
        
    async def selectReview(self, interaction:discord.Interaction, select:discord.ui.Select=None):
        select = self.select
        print("selected review:", select.values[0])
        review = self.reviews[select.values[0]]
        user = await self.letterboxd.fetchMemberFromId(int(select.values[0]))
        embed, view = self.letterboxd.createReviewEmbed(data=review, user=user, interaction=interaction)
        await interaction.response.edit_message(embed=embed, view=view)


    @discord.ui.button(label="See other reviews", style=discord.ButtonStyle.primary)
    async def seeOtherReviews(self,interaction:discord.Interaction, button:discord.ui.Button):
        film = self.film
        reviews = self.reviews

        embed = discord.Embed(title=f"{film['film']["title"]}", colour=discord.Colour.blurple(), url=film["film"]["link"])
        embed.set_thumbnail(url=self.film["film"]["images"]["poster"])
        embed.set_image(url=self.film["film"]["images"]["backdrop"])
        options = []

        for i in range(len(reviews)):
            userId = list(reviews.keys())[i]
            review = reviews[userId] # fetches user's review
            user = self.letterboxd.letterboxdDetails["users"][list(reviews.keys())[i]]["discord username"]
            if i > 25:
                pass # WIP: Add pagination

            embed.add_field(name=user, value=self.letterboxd.ratingEmojis(rating=float(review["member"]["rating"])), inline=False)
            options.append(discord.SelectOption(label=user, value=str(userId), description=f"{self.letterboxd.ratingEmojis(rating=float(review['member']['rating']))}"))

        selectReviewUI = discord.ui.View()
        selectReview:discord.ui.Select = discord.ui.Select(placeholder="Select a review", options=options)
        self.select = selectReview
        selectReview.callback = self.selectReview
        selectReviewUI.add_item(selectReview)

        await interaction.response.send_message(embed=embed, view=selectReviewUI)
    
    def changeUser(self, user:discord.Member):
        self.user = user
# Embeds
class letterboxdActivityEmbed(discord.Embed):
    def __init__(self, title = None, type = 'rich', url=None, timestamp = None, activity:list = None, user:discord.Member = None, letterboxd:letterboxd = None):
        super().__init__(colour=discord.Colour.blurple(), title=title, type=type, url=url, description=None, timestamp=timestamp)
        self.activity = activity
        self.user = user

        self.letterboxd = letterboxd

        self.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        self.description = self.buildDescription()
        self.set_footer(text="Setup tracking with /letterboxd_login", icon_url=letterboxdLogo)

    def buildDescription(self) -> str:
        description = ""
        for film in self.activity:
            description += f"[{film['film']["title"]}]({film["member"]['link']}) - {self.letterboxd.ratingEmojis(film['member']['rating'])} \n"
        return description

class letterboxdFilmEmbed(discord.Embed):
    def __init__(self, letterboxd:letterboxd, title = None, type = 'rich', url = None, timestamp = None, rating = None, review = None, watchDate=None, images = [None, None], author:discord.Member = None, data:dict = None, spoiler:bool = False, ):
        super().__init__(colour=None, title=title, type=type, url=url, description=None, timestamp=timestamp)

        if data != None:
            self.buildFromResponse(data, author)
        else:
            self.rating = float(rating)
            self.review = review
            self.poster = images[0]
            self.backdrop = images[1]
            self.spoiler = spoiler
            self.watchDate = watchDate
        self.letterboxd = letterboxd
        self.set_author(name=author.display_name, icon_url=author.display_avatar.url)

        if self.poster != None:
            self.set_thumbnail(url=self.poster)
        if self.backdrop != None:
            self.set_image(url=self.backdrop)
        
        if self.rating != None:
            self.add_field(name="Rating", value=self.letterboxd.ratingEmojis(self.rating), inline=False)
        
        if self.watchDate != None:
            self.add_field(name="Watched", value=self.watchDate, inline=True)

        if self.review != None:
            if self.spoiler:
                self.add_field(name="", value=f"**This review has spoilers. If you want to read the review, click [here]({self.url})**", inline=False)
            else:
                paragraphs = self.review.split("\\n")
                length = len(paragraphs)
                print(length)
                if length > 23:
                    length = 23
                    self.insert_field_at(0, name="", value=f"Read full review [here]({self.url})", inline=False)
                for i in range(length):
                    if len(paragraphs[i]) > 1024:
                        final = paragraphs[i].split()[-1]
                        paragraphs[i] = " ".join(paragraphs[i].split()[:-1]) # What the fuck? Need to test this, because not sure if :-1 is the same as :1024.
                        paragraphs[i+1] = final + " " + paragraphs[i+1]
                    self.add_field(name ="", value=paragraphs[i], inline=False)

        self.set_footer(text="Setup tracking with /letterboxd_login", icon_url=letterboxdLogo)
        self.setColour(self.rating)

    def buildFromResponse(self, data:dict, user:discord.Member):
        print(f"building from {data}")
        self.title = data["film"]["title"]
        self.url = data["member"]["link"]
        self.rating = float(data["member"]["rating"])
        self.review = data["member"]["review"]
        self.poster = data["film"]["images"]["poster"]
        self.backdrop = data["film"]["images"]["backdrop"] 
        self.watchDate = data["member"]["watchdate"]
        
        if "This review may contain spoilers." in self.review:
            self.spoiler = True
        else:
            self.spoiler = False

    def setColour(self, rating):
        if rating <= 2:
            self.colour = discord.Colour.red()
        elif rating <= 3.5:
            self.colour = discord.Colour.orange()
        elif rating <= 4.5:
            self.colour = discord.Colour.green()
        else:
            self.colour = discord.Colour.gold()

class profileEmbed(discord.Embed):
    def __init__(self, colour = None, type = 'rich', url = None, description = None, ):
        super().__init__(colour=colour, type=type, url=url, description=description)



async def setup(bot):
    await bot.add_cog(letterboxd(bot))