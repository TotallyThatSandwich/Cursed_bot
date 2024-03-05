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

genericAI = ChatBot("genericAI")
trainer = ListTrainer(genericAI)

class genericAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "1210389365185056818" in message.content or "1210512184103403530" in message.content:
            response = genericAI.get_response(message.content)
            await message.channel.send(response)
        elif "reply" in str(message.type) and ["1210389365185056818", "1210512184103403530"] in message.mentions:
            response = genericAI.get_response(message.content)
            await message.channel.send(response)
    
    @app_commands.command(name="train_bot", description="Train the bot with the last x messages in the channel")
    @app_commands.describe(limit = "How many messages should the bot be trained with?")
    async def trainMessageData(self, interaction: discord.Interaction, limit: int = None):
        if limit > 50 or limit == None:
            return await interaction.response.send_message("Limit must be less than 50 or not empty")
        messageTrain = interaction.channel.history(limit=limit)

        formattedMessageTrain = []
        for i in messageTrain:
            formattedMessageTrain.append(str(i).lower())
        
        trainer.train(formattedMessageTrain)

async def setup(bot):
    await bot.add_cog(genericAI(bot))