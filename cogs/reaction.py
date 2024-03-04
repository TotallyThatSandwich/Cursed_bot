import discord
from discord.ext import commands
import os
import random
import asyncio
import sys

sys.path.append(os.path.abspath("../"))

import settings 
logger = settings.logging.getLogger("bot")

nerds = ["https://tenor.com/view/nerd-emoji-nerd-emoji-avalon-play-avalon-gif-24241051", "https://tenor.com/view/pon-gif-15097379091171620462"]

class react(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        messageContent = str(message.content)

        if "reply" in str(message.type):
            if not ("*" in messageContent and len(messageContent) > 1 and " " not in messageContent):
                return
            # 75% chance to react
            if random.randint(1, 100) <= 75:
                await message.reply(random.choice(nerds))
            else:
                return
        else:
            logger.info(message, message.type)


async def setup(bot):
    await bot.add_cog(react(bot))