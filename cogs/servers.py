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
    async def server_info(self, interaction: discord.Interaction, server_name: str = None):
            if server_name is None:
                server_name = interaction.channel.name

            with open("servers.json", "r") as f:
                servers = json.load(f)

            try:

                name = server_name.lower()

                address = servers[name]["link"]
                whitelist = servers[name]["whitelist"]
                rules = servers[name]["rules"]
                colour = servers[name]["colour"]
                img = servers[name]["img"]
                port = int(servers[name]["port"])

                sock.settimeout(15)
                result = sock.connect_ex((address,port))

                if result == 0:
                    status =  'UP'
                else:
                    status = 'DOWN'

                rules_str = "\n".join(rules)

                embed = discord.Embed(title=f"{name}", description=f"Server Address: {address}", color=discord.colour.parse_hex_number(colour))
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

    @app_commands.command(name="port_checker", description="Port Check")
    async def port_checker(self, interaction: discord.Interaction, ip: str, port: str):
        sock.settimeout(2)
        result = sock.connect_ex((ip,int(port)))

        if result == 0:
            await interaction.response.send_message(f"Port {port} is open on {ip}")
        else:
            await interaction.response.send_message(f"Port {port} is closed on {ip}")

    @app_commands.command(name="channel_test", description="Port Check")
    async def channel_test(self, interaction: discord.Interaction):
        await interaction.response.send_message(interaction.channel.name)
async def setup(bot):
    await bot.add_cog(Servers(bot))
