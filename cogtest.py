import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


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

bot.run(token)