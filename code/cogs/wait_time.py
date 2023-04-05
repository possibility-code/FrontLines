import discord
from discord.ext import commands
from discord import app_commands
import datetime

"""
Allow admins to view the wait time for a specific date and hour

Can only be run within 2 servers, can be changed though
"""
class wait_time(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot


    # Command to allow managers to view the wait time of a current hour on a current day
    @app_commands.command()
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(573919902042423317), discord.Object(977410826233344040))
    @app_commands.describe(date="Date, EX: 2022-05-27")
    @app_commands.describe(hour="Specific hour within the day (in 24 hour time), EX: 16")
    async def waittime(self, interaction: discord.Interaction, date: str, hour: int):
        """Get the wait time of a certain date at a specific hour"""
        try:
            async with self.bot.db.acquire() as conn:
                wait_time = await conn.fetchval("SELECT wait_time FROM wait_time WHERE date = $1 AND hour = $2", datetime.datetime.strptime(date, "%Y-%m-%d"), hour)
        # If the user inputs random shit, the datetime parser will throw an error, 
        # so we catch it and return a message
        except:
            embed = discord.Embed(
                title="Not Found",
                description=f"There was no entry found for the date {date} and hour {hour}.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        # If there is no wait time, return a message alerting the user
        if not wait_time:
            embed = discord.Embed(
                title="Not Found",
                description=f"There was no entry found for the date {date} and hour {hour}.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        # Otherwise, return the wait time
        embed = discord.Embed(
            title="Wait Time",
            description=f"The wait time for {date} at {hour} was {wait_time}."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
	await bot.add_cog(wait_time(bot))