import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import sys
import aiofiles
import requests

sys.path.append(os.path.abspath("../"))

import settings as settings

logger = settings.logging.getLogger("bot")

class GCYT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.retrieve_videos.start()

    @tasks.loop(hours=1)
    async def retrieve_videos(self):
        video = await self.retrieveNewestGCGSVideo()
        if video != None:
            try:
                channel = self.bot.get_channel(int(settings.GCYTC))
                await channel.send(video)
            except Exception as e:
                logger.info(e)
        else:
            logger.info("no new videos")

    async def retrieveNewestGCGSVideo(self):
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

        saved_video_id = await self.read_saved_video_id()
        if videoID != saved_video_id:
            await self.save_video_id(videoID)
            return "https://www.youtube.com/watch?v=" + videoID
        else:
            return None
    
    async def save_video_id(self, video_id):
        async with aiofiles.open("../latest_video_id.txt", "w") as f:
            await f.write(video_id)

    async def read_saved_video_id(self):
        try:
            async with aiofiles.open("../latest_video_id.txt", "r") as f:
                return (await f.read()).strip()
        except FileNotFoundError:
            return None
        
    @app_commands.command(name="latest_video", description="Get latest GCGS youtube video")
    async def getLatestVideo(self, interaction: discord.Interaction):
        video = await self.retrieveNewestGCGSVideo()
        
        if video != None:
            try:
                channel = self.bot.get_channel(int(settings.GCYTC))
                await channel.send(video)

            except Exception as e:
                logger.info(e)
                await interaction.response.send_message(video)

        else:
            videoID = await self.read_saved_video_id()
            video = "https://www.youtube.com/watch?v=" + videoID

            try:
                channel = self.bot.get_channel(int(settings.GCYTC))
                await channel.send(video)

            except Exception as e:
                logger.info(e)
                await interaction.response.send_message(video)

async def setup(bot):
    await bot.add_cog(GCYT(bot))