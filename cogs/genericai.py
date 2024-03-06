import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import sys
import nltk
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

class genericAI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot,

    @commands.Cog.listener()
    async def on_message(self, message):
        botQuery = str(message.content)
        if "1210389365185056818" in message.content or "1210512184103403530" in message.content and not(message.author.id in ["1210389365185056818", "1210512184103403530"]):
            if "1210389365185056818" in botQuery:
                botQuery = botQuery.replace(f"<@1210389365185056818>", "")
            else:
                botQuery = botQuery.replace(f"<@1210512184103403530>", "")
            
            botQuery = botQuery.replace("", "")
            response = str(genericChatBot.get_response(botQuery))

            if "1210389365185056818" in response:
                response = response.replace("<@1210389365185056818>", "")
            else:
                response = response.replace("<@1210512184103403530>", "")

            if "@" in response:
                response = response.split("@")
                response = "".join(response)

            print(response)

            await message.channel.send(response)

        elif "reply" in str(message.type) and "1210389365185056818" in message.mentions or "1210512184103403530" in message.mentions:
            await message.channel.send(response)
    
    @app_commands.command(name="train_bot", description="Train the bot with the last x messages in the channel")
    @app_commands.describe(limit = "How many messages should the bot be trained with?")
    async def trainMessageData(self, interaction: discord.Interaction, limit: int = None):
        if limit > 200 or limit == None:
            return await interaction.response.send_message("Limit must be less than 50 or not empty")
        
        messageElement = []
        formattedMessageTrain = []
        history = interaction.channel.history(limit=limit)
        
        async for i in history:
            if not(i.author.id in ["1210389365185056818", "1210512184103403530"]):
                if "reply" in str(i.type):
                    repliedMessage = await interaction.channel.fetch_message(i.reference.message_id)
                    formattedMessageTrain.append([repliedMessage, i])
        
        try:
            for i in range(formattedMessageTrain):
                trainer.train(formattedMessageTrain[i])
        except Exception as e:
            await interaction.response.send_message(f"An error occured: {e}")
        await interaction.response.send_message("Training complete")

async def setup(bot):
    await bot.add_cog(genericAI(bot))
