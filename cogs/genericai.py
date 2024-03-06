import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import os
import asyncio
import sys
import nltk 
from nltk import pos_tag
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import settings as settings
logger = settings.logging.getLogger("bot")

genericChatBot = ChatBot("GenericBot")
trainer = ListTrainer(genericChatBot)

conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]
trainer.train(conversation)

class botView(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) not in settings.DEV:
                return await interaction.response.send_message("You do not have permission to use this command", delete_after=5)
        
        try:
            os.remove("db.sqlite3")
        except Exception as e:
            return await interaction.response.send_message(f"An error occured: {e}")
        
        await interaction.response.send_message(content="Database has been deleted. Please run ``?reload genericai`` to generate the database again.", ephemeral=True, delete_after=10)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.blurple)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Cancelled deletion.", ephemeral=True, delete_after=5)

class genericAI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot,

    @commands.Cog.listener()
    async def on_message(self, message):
        botQuery = str(message.content)

        if "1210389365185056818" in botQuery:
            botQuery = botQuery.replace(f"<@1210389365185056818>", "")
        else:
            botQuery = botQuery.replace(f"<@1210512184103403530>", "")

        async def formatResponse(query):
            response = str(genericChatBot.get_response(query))
            if "1210389365185056818" in response:
                    response = response.replace("<@1210389365185056818>", "")
            else:
                response = response.replace("<@1210512184103403530>", "")
            
            if "@" in response:
                response = response.split("@")
                response = "".join(response)

            return response

        # checks if someone is mentioning the bot
        if "1210389365185056818" in message.content or "1210512184103403530" in message.content and not(message.author.id in ["1210389365185056818", "1210512184103403530"]):
            response = await formatResponse(botQuery)
            await message.channel.send(response)

        elif "reply" in str(message.type) and "1210389365185056818" in message.mentions or "1210512184103403530" in message.mentions:
            reference = message.reference.message_id
            if reference.author.id in ["1210389365185056818", "1210512184103403530"]:
                response = await formatResponse(botQuery)
                return await message.channel.send(response)
        

    
    @app_commands.command(name="train_bot", description="Train the bot with the last x messages in the channel")
    @app_commands.describe(limit = "How many messages should the bot be trained with?")
    async def trainMessageData(self, interaction: discord.Interaction, limit: int):
        
        try:
            with open("blacklist.txt", "r") as blacklist:
                blacklist = blacklist.readlines()
                for i in blacklist:
                    if i == interaction.user.id:
                        return await interaction.response.send_message("You are blacklisted from training the bot", ephemeral=True)
        except:
            pass
        
        history = interaction.channel.history(limit=limit)
        finalMessageTrain = []

        async for i in history:
            if not(i.author.id in ["1210389365185056818", "1210512184103403530"]):
                if "reply" in str(i.type):
                    repliedMessage = await interaction.channel.fetch_message(i.reference.message_id)
                    finalMessageTrain.append([repliedMessage.content, i.content])
               
        try:
            for i in range(len(finalMessageTrain)):
                beautify = "\n".join(finalMessageTrain[i])
                logger.info(f"Training bot with:[\n{beautify}]\n") 
                print(f"Training bot with: {finalMessageTrain[i]}")
                trainer.train(finalMessageTrain[i])
        except Exception as e:
            await interaction.response.send_message(f"An error occured: {e}")
        await interaction.response.send_message("Training complete", delete_after=5)

    @app_commands.command(name="blacklist_user", description="block a user from training the bot")
    @app_commands.describe(user = "The user to block")
    async def blacklistUser(self, interaction: discord.Interaction, user: discord.User):
        if str(interaction.user.id) not in settings.DEV:
            return await interaction.response.send_message("You do not have permission to use this command")
        
        blacklist = open("blacklist.txt", "a")
        blacklist.write(f"{user.id}\n")
        blacklist.close()
        
        await interaction.response.send_message(f"User {user.name} has been blacklisted")

    @app_commands.command(name="unblacklist_user", description="unblock a user from training the bot")
    @app_commands.describe(user = "The user to unblock")
    async def unblacklistUser(self, interaction: discord.Interaction, user: discord.User):
        if str(interaction.user.id) not in settings.DEV:
            return await interaction.response.send_message("You do not have permission to use this command")
        
        blacklist = open("blacklist.txt", "r")
        blacklist = blacklist.readlines()
        for i in blacklist:
            if i == user.id:
                blacklist.remove(i)
        
        blacklist = open("blacklist.txt", "w")
        blacklist.write("".join(blacklist, "\n"))
        blacklist.close()

        await interaction.response.send_message(f"User {user.name} has been unblacklisted")

    @app_commands.command(name="delete_database", description="Delete the bot's database")
    async def deleteDatabase(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Are you sure?", description="This action is irreversible", color=discord.Color.red())

        await interaction.response.send_message(embed=embed, ephemeral=True, view=botView(), delete_after=30)
    
async def setup(bot):
    await bot.add_cog(genericAI(bot))
    
