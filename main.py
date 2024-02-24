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
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Hazbin Hotel"))

    for cog_file in os.listdir('./cogs'):
            if cog_file.endswith(".py"):
                await bot.load_extension(f"cogs.{cog_file[:-3]}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

# kick kosta command
@bot.event
async def on_member_join(member):
   if str(member.id) in settings.BLACKLIST:

       kick_delay = random.randint(300, 43200)
       hours, remainder = divmod(kick_delay, 3600)
       minutes, seconds = divmod(remainder, 60)

       channel = bot.get_channel(settings.GENERAL)
       kick_msg = f'{member.mention} will be kicked in {hours} hours and {minutes} minutes.'

       await channel.send(kick_msg)

       logger.info(f"kicking in {kick_delay/60} minutes")

       await asyncio.sleep(kick_delay)
       await member.kick(reason="womp womp")

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


@bot.tree.command(name="latest_video")
async def getLatestVideo(interaction: discord.Interaction):
    video = await retrieveNewestGCGSVideo()
    
    try:
        channel = bot.get_channel(settings.GCYTC)
        await channel.send(video)
    except Exception as e:
        logger.info(e)
        await interaction.response.send_message(video)



bot.run(settings.TOKEN, root_logger=True)
