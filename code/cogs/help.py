import discord
from discord.ext import commands
from discord import app_commands

"""
Provides an embed containing all of the commands for the bot, and how to use them
"""
class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    async def help(self, interaction: discord.Interaction):
        """Get a list of all of the commands for the bot and how to use them"""
        embed = discord.Embed(
            title="Help"
        )
        embed.add_field(name="`/info`", value="Information regarding the bot's privacy policy and terms of service", inline=False)
        embed.add_field(name="`/timezoneset`", value="Set your time zone so that the bot knows what time to send your reminders at", inline=False)
        embed.add_field(name="`/remind`", value="Set a reminder for yourself", inline=False)
        embed.add_field(name="`/requestsupport`", value="Request live support with the bot from a member of the Possibility Support Team", inline=False)
        embed.add_field(name="`/setup`", value="ONLY ADMINS: Set up the bot for your server", inline=False)
        embed.add_field(name="`/thankyou`", value="Thank someone for their kind deeds - and optionally provide a reason", inline=False)
        embed.add_field(name="`/waiver`", value="Get a DM containing the bot's waiver - this can be used to change your answers or set them for the first time", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(help(bot))