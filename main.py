import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from typing import Literal
import asyncio
import random

blacklisted_users = ['695852014961164300']

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


## set status command
@bot.tree.command(name="set_status")
@app_commands.describe(statustext = "what should my status say?")
async def set_status(interaction: discord.Interaction, statustype: Literal['watching', 'playing'] , statustext: str):
    try:
        if statustype == 'watching':
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=statustext))
        else:
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=statustext))
        await interaction.response.send_message(f"status set to {statustype} {statustext}", ephemeral=True)
    except:
        await interaction.response.send_message(f"faild to set status", ephemeral=True)

## kick kosta command
@bot.event
async def on_member_join(member):
    if str(member.id) in blacklisted_users:

        kick_delay = random.randint(300, 43200)
        hours, remainder = divmod(kick_delay, 3600)
        minutes, seconds = divmod(remainder, 60)

        channel = bot.get_channel(1024094820706287697)
        kick_msg = f'{member.display_name} will be kicked in {hours} hours and {minutes} minutes.'

        await channel.send(kick_msg)

        print(f"kicking in {kick_delay/60} minutes")

        await asyncio.sleep(kick_delay)
        await member.kick(reason="womp womp")


bot.run(token)