import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import sys
import nltk 
from nltk import pos_tag
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

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

class genericAI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot,

    @commands.Cog.listener()
    async def on_message(self, message):
        botQuery = str(message.content)
        if "1210389365185056818" in message.content or "1210512184103403530" in message.content and not(message.author.id in ["1210389365185056818", "1210512184103403530"]):
            try:
                botQuery = botQuery.replace(f"<@1210389365185056818>", "")
            except:
                botQuery = botQuery.replace(f"<@1210512184103403530>", "")
            
            response = str(genericChatBot.get_response(botQuery))
            try:
                response = response.replace("<@1210389365185056818>", "")
            except:
                response = response.replace("<@1210512184103403530>", "")
            
            await message.channel.send(response)

        elif "reply" in str(message.type) and "1210389365185056818" in message.mentions or "1210512184103403530" in message.mentions:
            await message.channel.send(response)
    
    @app_commands.command(name="train_bot", description="Train the bot with the last x messages in the channel")
    @app_commands.describe(limit = "How many messages should the bot be trained with?")
    async def trainMessageData(self, interaction: discord.Interaction, limit: int = None):
        if limit > 50 or limit == None:
            return await interaction.response.send_message("Limit must be less than 50 or not empty")
        messageTrain = interaction.channel.history(limit=limit)

        formattedMessageTrain = []
        async for i in messageTrain:
            formattedMessageTrain.append(str(i).lower())
        
        try:
            trainer.train(formattedMessageTrain)
        except Exception as e:
            return await interaction.response.send_message(f"An error occured: {e}")
        return await interaction.response.send_message("Training complete")

async def setup(bot):
    await bot.add_cog(genericAI(bot))