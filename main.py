from discord.ext import commands
import discord
import os
import asyncio
import random
import requests
import settings

logger = settings.logging.getLogger("bot")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="for /set_status"))

    for cog_file in os.listdir('./cogs'):
            if cog_file.endswith(".py"):
                await bot.load_extension(f"cogs.{cog_file[:-3]}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

## Retrieve new GCGS video
async def retrieveNewestGCGSVideo():
    URL = "https://www.googleapis.com/youtube/v3/channels"
    channelID = "UCG6DkyglRHZxtTP65FDgj1w"
    youtubeAPIkey = os.getenv("GOOGLEAPI")
    fetchParameters = {
         "part":"contentDetails",
         "id": channelID,
         "key": youtubeAPIkey}

    response = requests.get(url= URL, params=fetchParameters)
    response = response.json()
    
    playlistID = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    URL = "https://www.googleapis.com/youtube/v3/playlistItems"
    fetchParameters = {
        "part": "contentDetails",
        "playlistId": playlistID,
        "maxResults": 1,
        "key": youtubeAPIkey
    }

    response = requests.get(url=URL, params=fetchParameters)
    response = response.json()
    

    videoID = response["items"][0]["contentDetails"]["videoId"]

    return "https://www.youtube.com/watch?v=" + videoID


@bot.tree.command(name="latest_video", description="Get latest GCGS youtube video")
async def getLatestVideo(interaction: discord.Interaction):
    video = await retrieveNewestGCGSVideo()
    
    try:
        channel = bot.get_channel(int(settings.GCYTC))
        await channel.send(video)
    except Exception as e:
        logger.info(e)
        await interaction.response.send_message(video)



bot.run(settings.TOKEN, root_logger=True)
