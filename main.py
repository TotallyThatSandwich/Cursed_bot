import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from typing import Literal
import asyncio
import random

import requests
import googleapiclient

load_dotenv()
token = os.getenv("TOKEN") 
blacklisted_users = os.getenv("BLACKLIST")
general_channel = os.getenv("GENERAL")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Hazbin Hotel"))

    for cog_file in os.listdir('./cogs'):
            if cog_file.endswith(".py"):
                await bot.load_extension(f"cogs.{cog_file[:-3]}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

## kick kosta command
@bot.event
async def on_member_join(member):
    if str(member.id) in blacklisted_users:

        kick_delay = random.randint(300, 43200)
        hours, remainder = divmod(kick_delay, 3600)
        minutes, seconds = divmod(remainder, 60)

        channel = bot.get_channel(general_channel)
        kick_msg = f'{member.mention} will be kicked in {hours} hours and {minutes} minutes.'

        await channel.send(kick_msg)

        print(f"kicking in {kick_delay/60} minutes")

        await asyncio.sleep(kick_delay)
        await member.kick(reason="womp womp")

## Retrieve new GCGS video
async def retrieveNewestGCGSVideo():
    URL = "GET https://www.googleapis.com/youtube/v3/channels"
    channelID = "UCG6DkyglRHZxtTP65FDgj1w"
    youtubeAPIkey = os.getenv("GOOGLEAPI")
    fetchParameters = [
        "?part=contentDetails",
        f"&id={channelID}",
        f"&key={youtubeAPIkey}"]

    response = await requests.get(url= URL, params="".join(fetchParameters))
    response.json()
    print(response)

@bot.tree.command(name="Get GCGSYTC latest video")
async def getLatestVideo(interaction: discord.Interaction):
    retrieveNewestGCGSVideo()



bot.run(token)