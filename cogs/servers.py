import sys
import os
import traceback
import discord
from discord import app_commands
from discord.ext import commands
import json
import settings 
import socket

sys.path.append(os.path.abspath("../"))

logger = settings.logging.getLogger("bot")

class Servers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class addServer(discord.ui.Modal, title="add server"):
        server_name = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Server name",
            required=True,
            placeholder="Server Name"
        )

        address = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Server address",
            required=True,
            placeholder="Server address"
        )

        colour = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Colour",
            required=True,
            placeholder="Colour in hex e.g. `0x000000` for black"
        )

        img = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Thumbnail img",
            required=True,
            placeholder="url to img"
        )

        other = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="other",
        required=False,
        max_length=500,
        placeholder="Give any other info"
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with open("servers.json", "r") as f:
                servers = json.load(f)

            address, port = self.address.split(":")

            servers[self.server_name] = {
                "link": address,
                "port": port,
                "colour": self.colour,
                "img": self.img,
                "other": self.other
            }

            with open("servers.json", "w") as a:
                json.dump(servers, f, indent=4)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"An error occured: {e}", ephemeral=True)

        await interaction.response.send_message(f"Server {self.server_name} added", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error : Exception):
        traceback.print_tb(error.__traceback__)

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
                other = servers[name]["other"]
                colour = servers[name]["colour"]
                img = servers[name]["img"]
                port = int(servers[name]["port"])

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                sock.settimeout(15)
                result = sock.connect_ex((address,port))

                if result == 0:
                    status =  'UP'
                else:
                    status = 'DOWN'


                embed = discord.Embed(title=f"{name}", description=f"Server Address: {address}", color=discord.colour.parse_hex_number(colour))
                embed.set_thumbnail(url=img)

                if status == "DOWN":
                    embed.add_field(name="Status", value="```diff\n- Server is DOWN\n```", inline=False)
                else:
                    embed.add_field(name="Status", value="```diff\n+ Server is UP\n```", inline=False)

                embed.add_field(name="other", value=other, inline=False)

                await interaction.response.send_message(embed=embed)
            except Exception as e:
                await interaction.response.send_message(f"No server exists named {server_name}", ephemeral=True)
                logger.info(e)

    @app_commands.command(name="port_checker", description="Port Check")
    async def port_checker(self, interaction: discord.Interaction, ip: str, port: str):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(15)
        result = sock.connect_ex((ip,int(port)))

        if result == 0:
            await interaction.response.send_message(f"Port {port} is open on {ip}")
        else:
            await interaction.response.send_message(f"Port {port} is closed on {ip}")

    @app_commands.command(name="add_server", description="add server to server list")
    async def add_server(self, interaction: discord.Interaction):
        add_server = self.addServer()
        add_server.user = interaction.user
        await interaction.response.send_modal(add_server)
async def setup(bot):
    await bot.add_cog(Servers(bot))
