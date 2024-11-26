import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import sys

import json
import requests

from math import floor

from dateutil import tz
from datetime import datetime, time

date = datetime.now(tz=tz.tzlocal())
midnight = time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz.tzlocal())
letterboxdLogo = "https://a.ltrbxd.com/logos/letterboxd-decal-dots-pos-rgb-500px.png"

letterboxdDetails = {
    "chat": None,
    "users": {}
}
letterboxdURL = os.getenv("LETTERBOXD_URL")

import settings 
logger = settings.logging.getLogger("bot")

class letterboxdActivityEmbed(discord.Embed):
    def __init__(self, title = None, type = 'rich', url=None, timestamp = None, activity:list = None, user:discord.Member = None):
        super().__init__(colour=discord.Colour.blurple(), title=title, type=type, url=url, description=None, timestamp=timestamp)
        self.activity = activity
        self.user = user

        self.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        self.description = self.buildDescription()
        self.set_footer(text="Letterboxd watcher", icon_url=letterboxdLogo)

    def buildDescription(self) -> str:
        description = ""
        for film in self.activity:
            description += f"[{film['film']}]({film['link']}) - {film['member']['rating']}⭐\n"
        return description


class letterboxdFilmEmbed(discord.Embed):
    def __init__(self, title = None, type = 'rich', url = None, timestamp = None, rating = None, review = None, images = [None, None], author:discord.Member = None, data = None, spoiler:bool = False):
        super().__init__(colour=None, title=title, type=type, url=url, description=None, timestamp=timestamp)

        if data != None:
            self.buildFromResponse(data, author)
        else:
            self.rating = float(rating)
            self.review = review
            self.poster = images[0]
            self.backdrop = images[1]
            self.spoiler = spoiler
            
            
        self.set_author(name=author.display_name, icon_url=author.display_avatar.url)

        if self.poster != None:
            self.set_thumbnail(url=self.poster)
        if self.backdrop != None:
            self.set_image(url=self.backdrop)
        
        if self.rating != None:
            self.add_field(name="Rating", value=self.ratingEmojis(self.rating), inline=False)

        if self.review != None:
            if self.spoiler:
                self.add_field(name="", value=f"**This review has spoilers. If you want to read the review, click [here]({self.url})**", inline=False)
            else:
                paragraphs = self.review.split("\\n")
                length = len(paragraphs)
                print(length)
                if length > 24:
                    length = 24
                    self.insert_field_at(0, name="", value=f"Read full review [here]({self.url})", inline=False)
                for i in range(length):
                    if len(paragraphs[i]) > 1024:
                        final = paragraphs[i].split()[-1]
                        paragraphs[i] = " ".join(paragraphs[i].split()[:-1]) # What the fuck? Need to test this, because not sure if :-1 is the same as :1024.
                        paragraphs[i+1] = final + " " + paragraphs[i+1]
                    self.add_field(name ="", value=paragraphs[i], inline=False)

        self.set_footer(text="Letterboxd watcher", icon_url=letterboxdLogo)
        self.setColour(self.rating)

    def buildFromResponse(self, data, user:discord.Member):
        print(f"building from {data}")
        self.title = data["film"]
        self.url = data["link"]
        self.rating = float(data["member"]["rating"])
        self.review = data["member"]["review"]
        self.poster = data["images"]["poster"]
        self.backdrop = data["images"]["backdrop"] 
        
        if "This review may contain spoilers." in self.review:
            self.spoiler = True
        else:
            self.spoiler = False

    def ratingEmojis(self, rating) -> str:
        rating = float(rating)
        if rating.is_integer():
            return "⭐" * rating
        else:
            return ("⭐" * floor(rating)) + "½"

    def setColour(self, rating):
        if rating <= 2:
            self.colour = discord.Colour.red()
        elif rating <= 4:
            self.colour = discord.Colour.green()
        else:
            self.colour = discord.Colour.gold()

class letterboxd(commands.Cog):
    def __init__(self, bot:discord.Client):
        self.bot = bot
        self.letterboxdDetails = letterboxdDetails

        if os.path.exists("letterboxd.json"):
            with open("letterboxd.json", "r") as f:
                self.letterboxdDetails = json.load(f)


    async def fetchFromLetterboxd(self, user:discord.Member = None, letterboxdUser=None, amount=1) -> list:
        """
        Fetches ``amount`` of films for a ``user``'s discord id or ``letterboxdUser`` username
        """
        if user != None:
            try:
                user = self.letterboxdDetails["users"][str(user.id)]["username"]
                url = f"{letterboxdURL}/{user}?amount={amount}"
            except KeyError:
                return None
        elif letterboxdUser != None:
            url = f"{letterboxdURL}/{letterboxdUser}?amount={amount}"
        else:
            raise ValueError("Either a user or a letterboxd username must be provided")
            return None
        
        print(f"fetching from {url}")
        
        response = requests.get(url=url)
        response = response.json()

        return response["films"]

   
    @app_commands.command()
    async def letterboxd_setup(self, interaction:discord.Interaction, chat:discord.TextChannel):
        if not interaction.user.top_role.permissions.administrator:
            return await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)
        
        with open("letterboxd.json", "w") as f:
            self.letterboxdDetails["chat"] = chat.id
            json.dump(self.letterboxdDetails, f)
        await interaction.response.send_message(f"Letterboxd channel has been set to {chat.mention}", ephemeral=True)

    @app_commands.command(name="letterboxd_login", description="Opt in for Letterboxd tracking. Run this command again to opt out.")
    @app_commands.describe(letterboxdusername= "Your Letterboxd username or your Letterboxd profile URL")
    async def letterboxdLogin(self, interaction:discord.Interaction, letterboxdusername:str):
        if str(interaction.user.id) in self.letterboxdDetails["users"]:
            self.letterboxdDetails["users"].pop(str(interaction.user.id))

            with open("letterboxd.json", "w") as f:
                json.dump(self.letterboxdDetails, f)

            await interaction.response.send_message("You have opted out of Letterboxd tracking.", ephemeral=True)
        else:
            if "letterboxd.com" in letterboxdusername:
                letterboxdusername = letterboxdusername.split(".com/")[1].rstrip("/")
            
            response = await self.fetchFromLetterboxd(letterboxdUser=letterboxdusername, amount=5)
            
            self.letterboxdDetails["users"][interaction.user.id] = {
                "username": letterboxdusername,
                "activity": response
            }
            
            with open("letterboxd.json", "w") as f:
                json.dump(self.letterboxdDetails, f)

            await interaction.response.send_message("You have opted in for Letterboxd tracking.", ephemeral=True)

    @app_commands.command(name="fetch_latest_letterboxd", description="Fetch the latest Letterboxd activity")
    async def fetchLatestLetterBoxd(self, interaction:discord.Interaction, user:discord.Member=None):
        if user == None:
            user = interaction.user
            
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("You have not signed in for Letterboxd tracking", ephemeral=True)

        response = self.letterboxdDetails["users"][str(user.id)]["activity"][0]
        if response == None:
            return await interaction.response.send_message("There was an error fetching data. Has the user logged in with /letterboxd_login?", ephemeral=True)
        
        embed = letterboxdFilmEmbed(data=response[0], author=user)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fetch_letterboxd_activity", description="Fetch the latest Letterboxd activity")
    async def fetchLetterBoxdActivity(self, interaction:discord.Interaction, user:discord.Member=None):
        if user == None:
            user = interaction.user
            
        if not self.checkIfSignedIn(user):
            return await interaction.response.send_message("User have not signed in for Letterboxd tracking", ephemeral=True)
        
        response = self.letterboxdDetails["users"][str(user.id)]["activity"]
        embed = letterboxdActivityEmbed(activity=response, user=user)
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
            json.dump(self.letterboxdDetails, f)

        await interaction.response.send_message("Activity has been updated!", ephemeral=True)
        
    @tasks.loop(hours=1)
    async def getLetterboxd(self):
        for user in self.letterboxdDetails["users"]:
            url = f"{letterboxdURL}/{user}"

            response = await self.fetchFromLetterboxd(user=user["username"], amount=1)
            if response == None:
                return logger.error(f"Error fetching data for {user}")

            if response[0] != self.letterboxdDetails["users"][user]["activity"][0]:
                member = await self.bot.fetch_user(user)
                try:
                    embed = letterboxdFilmEmbed(data=response[0], author=member)
                    channel = self.bot.get_channel(self.letterboxdDetails["chat"])
                    await channel.send(embed=embed)
                except Exception as e:
                    logger.error(e)
                    return
                

                self.letterboxdDetails["users"][user] = response[0]

                with open("letterboxd.json", "w") as f:
                    json.dump(self.letterboxdDetails, f)

    @tasks.loop(time=midnight)
    async def getLast5(self):
        if date.weekday() == 4:
            for user in self.letterboxdDetails["users"]:
                url = f"{letterboxdURL}/{user}?amount=5"

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
    



async def setup(bot):
    await bot.add_cog(letterboxd(bot))