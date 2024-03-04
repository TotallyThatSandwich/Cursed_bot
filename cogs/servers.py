import sys
import os
import discord
from discord import app_commands
from discord.ext import commands
import json
import settings 
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

result = sock.connect_ex(('127.0.0.1',80))

sys.path.append(os.path.abspath("../"))

logger = settings.logging.getLogger("bot")

class Servers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server_info", description="Show game Server Info")
    @app_commands.describe(server_name="name of server to display info on")
    async def server_info(self, interaction, server_name: str):
        try:
            with open("servers.json", "r") as f:
                servers = json.load(f)

            address = servers[server_name]["link"]
            whitelist = servers[server_name]["whitelist"]
            rules = servers[server_name]["rules"]
            colour = servers[server_name]["colour"]
            img = servers[server_name]["img"]
            port = int(servers[server_name]["port"])

            sock.settimeout(2)
            result = sock.connect_ex((address,port))

            if result == 0:
                status =  'UP'
            else:
                status = 'DOWN'

            rules_str = "\n".join(rules)

            embed = discord.Embed(title=server_name, description=f"Server Address: {address}", color=discord.colour.parse_hex_number(colour))
            embed.set_thumbnail(url=img)
            embed.add_field(name="Whitelist", value=whitelist, inline=False)

            if status == "DOWN":
                embed.add_field(name="Status", value="```diff\n- Server is DOWN\n```", inline=False)
            else:
                embed.add_field(name="Status", value="```diff\n+ Server is UP\n```", inline=False)

            embed.add_field(name="Rules", value=rules_str, inline=False)

            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message(f"No server exists named {server_name}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servers(bot))
