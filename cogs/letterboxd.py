import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import sys
import nltk
from nltk import pos_tag


nltk.download('averaged_perceptron_tagger')


sys.path.append(os.path.abspath("../"))

import settings 
logger = settings.logging.getLogger("bot")

class letterboxd(commands.Cog):
    pass

async def setup(bot):
    await bot.add_cog(letterboxd(bot))