import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()
token = os.getenv("TOKEN") 

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Hazbin Hotel"))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="set_status")
@app_commands.describe(statustext = "what should my status say?")
async def set_status(interaction: discord.Interaction, statustype: Literal['watching', 'playing'] , statustext: str):
    if statustype == 'watching':
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=statustext))
    else:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=statustext))

bot.run(token)