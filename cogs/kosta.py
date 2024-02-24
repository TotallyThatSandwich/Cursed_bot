import discord
from discord.ext import commands
import os
import random
import asyncio

import settings

logger = settings.logging.getLogger("bot")

class Kosta(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(member, self):

        #logger.info(f"blacklist: {settings.BLACKLIST}")
        #logger.info(f"channel: {self.bot.get_channel(settings.GENERAL)}")

        if str(member.id) in settings.BLACKLIST:

            kick_delay = random.randint(300, 43200)
            hours, remainder = divmod(kick_delay, 3600)
            minutes, seconds = divmod(remainder, 60)

            channel = self.bot.get_channel(settings.GENERAL)
            kick_msg = f'{member.mention} will be kicked in {hours} hours and {minutes} minutes.'

            await channel.send(kick_msg)

            print(f"kicking in {kick_delay/60} minutes")

            await asyncio.sleep(kick_delay)
            await member.kick(reason="womp womp")

async def setup(bot):
    await bot.add_cog(Kosta(bot))