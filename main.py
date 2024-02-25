from discord.ext import commands
import discord
import os
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
        
bot.run(settings.TOKEN, root_logger=True)
