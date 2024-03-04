import discord
from discord.ext import commands
import os
import random
import asyncio
import sys

sys.path.append(os.path.abspath("../"))

import settings 
logger = settings.logging.getLogger("bot")

nerds = ["https://tenor.com/view/nerd-emoji-nerd-emoji-avalon-play-avalon-gif-24241051", "https://tenor.com/view/pon-gif-15097379091171620462"]

class react(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        messageContent = str(message.content)

        
        # Use this if condition for any messages that are replying to others. These listeners don't listen for the bot itself.
        if "reply" in str(message.type) and not(str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
            if "*" in messageContent and len(messageContent) > 1 and " " not in messageContent:
                # 75% chance to react
                if random.randint(1, 100) <= 75:
                    await message.reply(random.choice(nerds))
                else:
                    return
            elif "based" in messageContent and len(messageContent.split()) == 1:
                if random.randint(1, 2) == 1:
                    await message.reply("\"Based\"? Are you fucking kidding me? I spent a decent portion of my life writing all of that and your response to me is \"Based\"? Are you so mentally handicapped that the only word you can comprehend is \"Based\" - or are you just some fucking asshole who thinks that with such a short response, he can make a statement about how meaningless what was written was? Well, I'll have you know that what I wrote was NOT meaningless, in fact, I even had my written work proof-read by several professors of literature. Don't believe me? I doubt you would, and your response to this will probably be \"Based\" once again. Do I give a fuck? No, does it look like I give even the slightest fuck about five fucking letters? I bet you took the time to type those five letters too, I bet you sat there and chuckled to yourself for 20 hearty seconds before pressing \"send\". You're so fucking pathetic. I'm honestly considering directing you to a psychiatrist, but I'm simply far too nice to do something like that. You, however, will go out of your way to make a fool out of someone by responding to a well-thought-out, intelligent, or humorous statement that probably took longer to write than you can last in bed with a chimpanzee. What do I have to say to you? Absolutely nothing. I couldn't be bothered to respond to such a worthless attempt at a response. Do you want \"Based\" on your gravestone?")
                else:
                    return

        # Normal message listners go below
        
        if "crazy" in messageContent:
            if not(str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
                await message.reply("Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy.")
            else:
                if random.randint(1,2) == 1:
                    await message.reply("Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy.")

        if "I hate" in messageContent:
            word = messageContent.split("I hate")
            word = word[len(word)-1]

            word = word.split()

            if len(word) > 1:
                return
            
            finalFormattedWord = ""

            for i in word[0]:
                if i.isalpha():
                    finalFormattedWord = "".join([finalFormattedWord, i])
            if finalFormattedWord != "you":
                await message.reply(f"If {finalFormattedWord} has a million fans, then I am one of them. If {finalFormattedWord} has ten fans, then I am one of them. If {finalFormattedWord} has only one fan then that is me. If {finalFormattedWord} has no fans, then that means I am no longer on earth. If the world is against {finalFormattedWord}, then I am against the world.")
            else:
                await message.reply(f"If they have a million fans, then I am one of them. If they have ten fans, then I am one of them. If {finalFormattedWord} have only one fan then that is me. If they have no fans, then that means I am no longer on earth. If the world is against them, then I am against the world.")

async def setup(bot):
    await bot.add_cog(react(bot))