import discord
from discord.ext import commands
from discord import app_commands
import requests

class helldivers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_planet_info(self):
        planetsInfo = {}

        response = requests.get("https://api.genericcursed.com//api/801/status")
        if response.status_code == 200:
            info = response.json()
            
            for i in info["campaigns"]:

                planer_id = i["planet"]["index"]

                response_planet = requests.get(f"https://api.genericcursed.com//api/801/planets/{planer_id}/status")
                if response_planet.status_code == 200:
                    planet_info = response_planet.json()
                    
                    players = planet_info["players"]
                    owner = planet_info["owner"].lower()
                    liberation = planet_info["liberation"]
                    Name = planet_info["planet"]["name"]
                    regen_per_second = planet_info["regen_per_second"]
                    health = planet_info["health"]
                    max_health = planet_info["planet"]["max_health"]

                    planetsInfo[Name] = {
                        "players": players,
                        "owner": owner,
                        "liberation": liberation,
                        "regen_per_second": regen_per_second,
                        "health": health,
                        "max_health": max_health
                    }
                
                else:
                   return

        else:
            return

        return planetsInfo

    @app_commands.command(name="democtatic_status", description="get helldivers 2 campaign Status")
    async def democtaticStatus(self, interaction: discord.Interaction):

        await interaction.response.defer()

        planetsInfo = await self.get_planet_info()
        if planetsInfo:

            concurrent_players = 0

            for planet in planetsInfo:
                concurrent_players += planetsInfo[planet]["players"]

            embed = discord.Embed(title=f"", description=f"**Active Helldivers** • `{concurrent_players}`", color=discord.colour.parse_hex_number("0xffe80a"))
            embed.set_author(name="Galactic War Status", icon_url="https://pbs.twimg.com/profile_images/1453151436125126666/HJ4HhR6M_400x400.jpg")

            for planet in planetsInfo:

                players = planetsInfo[planet]["players"]
                liberation = round(planetsInfo[planet]["liberation"], 2)
                health = planetsInfo[planet]["health"]
                max_health = planetsInfo[planet]["max_health"]
                health_perc = (health / max_health) * 100
          
                if planetsInfo[planet]["owner"] == "terminids":
                    enemy = "<:terminid:1217749647431434362>"
                else: 
                    enemy = "<:automaton:1217749643945840690>"

                embed.add_field(name=f"¤ {planet}", value=f"◦ <:Helldivers:1217749645795655680> Active Helldivers •`{players}`\n◦ {enemy} Liberation • `{liberation}%`\n◦ :heart: Health • `{health}/{max_health}({round(health_perc, 2)}%)`", inline=False)

            await interaction.followup.send(embed=embed)

        else:
            await interaction.followup.send()(f"Failed to fetch planets data", ephemeral=True)

async def setup(bot):
    await bot.add_cog(helldivers(bot))