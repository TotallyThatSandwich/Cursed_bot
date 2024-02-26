from discord.ext import commands
from spellchecker import SpellChecker
import string

spell = SpellChecker()

class Annoying(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        slang = ["brb", "gtg", "joever", "rizz", "womp"]
        await self.bot.process_commands(message)
        if message.author != self.bot.user:
            words_spellchecked = []
            message_str = str(message.content)
            translator = str.maketrans('', '', string.punctuation)
            message_str.translate(translator)
            words = message_str.split(" ")
            for i in words:
                if i in slang:
                    words.remove(i)

            for word in words:
                words_spellchecked.append(spell.correction(word))

            for word in words_spellchecked:
                if word not in words:
                    await message.reply(f"{word}*")

async def setup(bot):
    await bot.add_cog(Annoying(bot))