from discord.ext import commands
import discord
import os
import settings
import git

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
        
@bot.command()
async def reload(ctx, cog: str):
    if f"{cog}.py" in os.listdir('./cogs') and str(ctx.message.author.id) in settings.DEV:
        try:
            await bot.reload_extension(f"cogs.{cog.lower()}")
            await ctx.send(f"reloaded {cog}")
        except:
            await ctx.send(f"an error ocured")
    elif str(ctx.message.author.id) in settings.DEV:
        await ctx.send(f"no cog exists named {cog}")
    else:
        await ctx.send(f"author is not a dev!")

@bot.command()
async def load(ctx, cog: str):
    if f"{cog}.py" in os.listdir('./cogs') and str(ctx.message.author.id) in settings.DEV:
        try:
            await bot.load_extension(f"cogs.{cog.lower()}")
            await ctx.send(f"reloaded {cog}")
        except:
            await ctx.send(f"an error ocured")
    elif str(ctx.message.author.id) in settings.DEV:
        await ctx.send(f"no cog exists named {cog}")
    else:
        await ctx.send(f"author is not a dev!")

@bot.command()
async def unload(ctx, cog: str):
    if f"{cog}.py" in os.listdir('./cogs') and str(ctx.message.author.id) in settings.DEV:
        try:    
            await bot.unload_extension(f"cogs.{cog.lower()}")
            await ctx.send(f"reloaded {cog}")
        except:
            await ctx.send(f"an error ocured")
    elif str(ctx.message.author.id) in settings.DEV:
        await ctx.send(f"no cog exists named {cog}")
    else:
        await ctx.send(f"author is not a dev!")
     
@bot.command()
async def gitPull(ctx):
    if str(ctx.message.author.id) in settings.DEV:
        g = git.cmd.Git(".")
        g.pull()
        await ctx.send("pulled")

bot.run(settings.TOKEN, root_logger=True)
