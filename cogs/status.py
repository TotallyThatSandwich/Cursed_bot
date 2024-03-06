import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal

class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_status", description="Set bots custom status")
    @app_commands.describe(statustext = "What should my status say?")
    async def set_status(self, interaction: discord.Interaction, statustype: Literal['watching', 'playing'] , statustext: str):
        try:
            if statustype == 'watching':
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=statustext))
            else:
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=statustext))
            await interaction.response.send_message(f"status set to {statustype} {statustext}", ephemeral=True)
        except:
            await interaction.response.send_message(f"faild to set status", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))