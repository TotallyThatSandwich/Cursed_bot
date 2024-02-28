import discord
from discord.ext import commands
import os
import random
import asyncio
import sys

sys.path.append(os.path.abspath("../"))

import settings 
logger = settings.logging.getLogger("bot")

class react(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        
        messageContent = str(message.content)

        if "*" in messageContent and "reply" in str(message.type):
            await message.reply("https://tenor.com/view/pon-gif-15097379091171620462")
        else:
            logger.info(message, message.type)


async def setup(bot):
    await bot.add_cog(react(bot))