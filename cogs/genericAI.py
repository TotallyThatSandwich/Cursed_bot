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

class genericAI(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if ["1210389365185056818", "1210512184103403530"] in message.content:
            response = genericAI.get_response(message.content)
            await message.channel.send(response)
        elif "reply" in str(message.type) and ["1210389365185056818", "1210512184103403530"] in message.mentions:
            response = genericAI.get_response(message.content)
            await message.channel.send(response)
    
    @app_commands.command()
    async def trainMessageData(self, ctx, limit):
        if limit > 50:
            return await ctx.send("Limit must be less than 50")
        messageTrain = ctx.channel.fetch_message(limit=limit)
        formattedMessageTrain = []
        for i in messageTrain:
            formattedMessageTrain.append(str(i).lower())

        trainer.train(formattedMessageTrain)

async def setup(bot):
    await bot.add_cog(genericAI(bot))