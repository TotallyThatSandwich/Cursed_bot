import discord

BOT_TOKEN = "MTIxMDM4OTM2NTE4NTA1NjgxOA.Grr2xY.8CRZvBFbxjbCqt7kfk-Jty1au5ntPkBorOLndQ"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(BOT_TOKEN)