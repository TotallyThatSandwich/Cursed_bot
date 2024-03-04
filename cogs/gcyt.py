import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import sys
import aiofiles
import requests
from datetime import datetime

sys.path.append(os.path.abspath("../"))

import settings as settings

logger = settings.logging.getLogger("bot")

class GCYT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtubeAPIkey = os.getenv("GOOGLEAPI")
        self.retrieve_videos.start()

    @tasks.loop(hours=1)
    async def retrieve_videos(self):
        videoID = await self.retrieveNewestGCGSVideo()

        if videoID != None:
            embed = await self.video_embed(videoID=videoID)

            try:
                channel = self.bot.get_channel(int(settings.GCYTC))
                await channel.send(embed=embed)
            except Exception as e:
                logger.info(e)
        else:
            logger.info("no new videos")

    async def retrieveNewestGCGSVideo(self):
        URL = "https://www.googleapis.com/youtube/v3/channels"
        channelID = "UCG6DkyglRHZxtTP65FDgj1w"
        fetchParameters = {
            "part":"contentDetails",
            "id": channelID,
            "key": self.youtubeAPIkey
        }

        response = requests.get(url= URL, params=fetchParameters)
        response = response.json()
        
        playlistID = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        URL = "https://www.googleapis.com/youtube/v3/playlistItems"
        fetchParameters = {
            "part": "contentDetails",
            "playlistId": playlistID,
            "maxResults": 1,
            "key": self.youtubeAPIkey
        }

        response = requests.get(url=URL, params=fetchParameters)
        response = response.json()

        videoID = response["items"][0]["contentDetails"]["videoId"]


        saved_video_id = await self.read_saved_video_id()
        if videoID != saved_video_id:
            await self.save_video_id(videoID)
            return videoID
        else:
            return None
    
    async def video_embed(self, videoID):
        URL = "https://www.googleapis.com/youtube/v3/videos"
        fetchParameters = {
            "part": "snippet",
            "id": videoID,
            "key": self.youtubeAPIkey
        }

        response = requests.get(url= URL, params=fetchParameters)
        response = response.json()

        title = response["items"][0]["snippet"]["title"]
        description = response["items"][0]["snippet"]["description"]
        thumbnail = response["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
        publishDate = response["items"][0]["snippet"]["publishedAt"]

        embed=discord.Embed(title=title, url="https://www.youtube.com/watch?v=" + videoID, description=description, color=0xc15d23, timestamp=datetime.strptime(publishDate, "%Y-%m-%dT%H:%M:%SZ"))
        embed.set_author(name="Generic Cursed Youtube Channel", url="https://www.youtube.com/@GenericCursedYTC", icon_url="https://yt3.googleusercontent.com/9tCKg_JTDrkkmkn6PBEDn-4FfGuDAfljGyw_9taAGWouDnSU7LJZ54G6izBm-AAYrGJ9ZpcMqA=s176-c-k-c0x00ffffff-no-rj")
        embed.set_thumbnail(url="https://yt3.googleusercontent.com/9tCKg_JTDrkkmkn6PBEDn-4FfGuDAfljGyw_9taAGWouDnSU7LJZ54G6izBm-AAYrGJ9ZpcMqA=s176-c-k-c0x00ffffff-no-rj")
        embed.set_footer(icon_url="https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png", text="Youtube")
        embed.set_image(url=thumbnail)

        return embed

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
        videoID = await self.retrieveNewestGCGSVideo()
        
        if videoID != None:
            embed = await self.video_embed(videoID=videoID)
            
            try:
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                logger.info(e)

        else:
            videoID = await self.read_saved_video_id()
            
            embed = await self.video_embed(videoID=videoID)

            try:
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                logger.info(e)

async def setup(bot):
    await bot.add_cog(GCYT(bot))
