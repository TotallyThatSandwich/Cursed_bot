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

randomCopypastas = ["If you shit in the sink at exactly 4:20 am and yell “amogus” 69 times,a shadowy figured called mom will come to beat you up and you will wake up in a place called the orphanage",
                    "My Grandfather smoked his whole life. I was about 10 years old when my mother said to him, 'If you ever want to see your grandchildren graduate, you have to stop immediately.'. Tears welled up in his eyes when he realized what exactly was at stake. He gave it up immediately. Three years later he died of lung cancer. It was really sad and destroyed me. My mother said to me- 'Don't ever smoke. Please don't put your family through what your Grandfather put us through.\" I agreed. At 28, I have never touched a cigarette. I must say, I feel a very slight sense of regret for never having done it, because your post gave me cancer anyway.",
                    "This is probably the worst thing I've ever seen. 100 years from now when I'm dying on a hospital bed and I'm asked what my biggest regret was it will be that I turned on my internet and scrolled through the internet on that fateful day... I will never be able to recover from this. No amount of therapy will save me. No amount of prescription pills will let me recover. I am a shell. This memory is so bad my brain is physically rejecting it and now I have a headache every time I think about it. Why did you post this, thinking it was a good idea? You've permanently ruined my life because of this, I hope you're happy. I hope that one day this gets branded as a war crime and you get hauled off to prison, never to see the light of day again. The fact that you're already not in a psych ward for insanity is so baffling I have lost all faith in every kind of justice system. If you subscribe to any religion, you'd best spend the rest of your time atoning for this ultimate sin. Have a terrible day, I hope this creation of yours haunts you in your dreams.",
                    ]
competitiveShooters = ["valorant", "counter strike"]


class react(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        messageContent = str(message.content).lower()

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

        if "i hate" in messageContent:
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

        if "bill" in messageContent and not (str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
            await message.reply("What the ♥♥♥♥ is wrong with this old bastard? Homeboy just straight up dies mid-level, the ♥♥♥♥ is this ♥♥♥♥? Dumb ♥♥♥♥ obviously missed the directions for the fountain of youth. Senile old ♥♥♥♥ can't even hold his own breath for 2 seconds without coughing up a lung, eat ♥♥♥♥ Bill. I like the science dude better.")
        
        if "sus" in messageContent and not (str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
            replies = ["STOP POSTING ABOUT AMONG US! I'M TIRED OF SEEING IT! My friends on TikTok send me memes, on Discord its fucking memes. I was in a server, right, and ALL the channels are just Among Us stuff. I showed my Champion underwear to my girlfriend, and the logo I flipped it and I said \"Hey babe, when the underwear sus! HAHA! Ding Ding Ding Ding Ding Ding Ding DiDiDing!\" I fucking looked at a trash can and I said \"Thats a bit sussy!\" I looked at my penis, I thought of the astronauts helmet and I go \"PENIS? MORE LIKE PEN-SUS!\" AAAAAAAAAAAAAA", 
                       "I can't fucking take it any more. Among Us has singlehandedly ruined my life. The other day my teacher was teaching us Greek Mythology and he mentioned a pegasus and I immediately thought 'Pegasus? more like Mega Sus!!!!' and I've never wanted to kms more. I can't look at a vent without breaking down and fucking crying. I can't eat pasta without thinking 'IMPASTA??? THATS PRETTY SUS!!!!' Skit 4 by Kanye West. The lyrics ruined me. A Mongoose, or the 25th island of greece. The scientific name for pig. I can't fucking take it anymore. Please fucking end my suffering.",
                       "Red sus. Red suuuus. I said red, sus, hahahahaha. Why arent you laughing? I just made a reference to the popular video game \"Among Us\"! How can you not laugh at it? Emergeny meeting! Guys, this here guy doesnt laugh at my funny Among Us memes! Lets beat him to death! Dead body reported! Skip! Skip! Vote blue! Blue was not an impostor. Among us in a nutshell hahahaha. What?! Youre still not laughing your ass off? I made SEVERAL funny references to Among Us and YOU STILL ARENT LAUGHING??!!! Bruh. Ya hear that? Wooooooosh. Whats woooosh? Oh, nothing. Just the sound of a joke flying over your head. Whats that? You think im annoying? Kinda sus, bro. Hahahaha! Anyway, yea, gotta go do tasks. Hahahaha!"]
            await message.reply(replies[random.randint(0,len(replies)-1)])
        
        if "touch grass" in messageContent and not(str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
            await message.reply("\"touch grass\" is not an insult towards gamers, rather it is advice for them. When participating in intense periods of gaming, the human hand has a tendency to get sweaty. The sweat causes the hand to become slick, and it b becomes more difficult to retain a grip on the gamers gaming mouse, thus making it more difficult to perform well in intense gaming moments. By touching grass with the gamers hand, the grass will impart a layer of particulate onto the gamers hand, the particulate can be made of a variety of dusts, dirts and other natural matter. This particulate will then act in a similar form to climbers chalk, absorbing the sweat and drying out the gamers hand. With dry hands, the gamer can now perform to their maximum when gaming. This is why when an enemy or teammate tells you to touch grass, they are simply trying to assist you in performing better.")
        
        if "is so good" in messageContent and str(message.channel.name).lower() in competitiveShooters:
            player = messageContent.split("is so good")

            print(player)
            player = player.split()

            playerName = ""
            for i in player[len(player)-1]:
                if str(i).isalpha():
                    playerName = "".join([playerName, i])
            
            print(playerName)

            await message.reply(f"This {playerName} player is fantastic. Just needs to work on communication, aim, map awareness, crosshair placement, economy management, pistol aim, awp flicks, grenade spots, smoke spots, pop flashes, positioning, bomb plant positions, retake ability, bunny hopping, spray control and getting a kill.")
        
        if random.randint(1, 100) == 1 and not(str(message.author.id) in ["1210389365185056818", "1210512184103403530"]):
            await message.reply(randomCopypastas[random.randint(0, len(randomCopypastas)-1)])

async def setup(bot):
    await bot.add_cog(react(bot))