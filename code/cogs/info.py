import discord
from discord.ext import commands
from discord import app_commands

"""
Provides the privacy policy and the terms of service for the bot
"""
class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    async def info(self, interaction: discord.Interaction):
        """Information regarding the bot's privacy policy and terms of service"""
        embed = discord.Embed(
            title="Information Regarding the Privacy Policy and Terms of Service for the FrontLines bot",
            description="**Privacy Policy**: By using our service, you hereby consent to the collection of data including, but not limited to: usernames, user IDs, guild IDs, channel IDs, role IDs, transcripts of tickets, and reasons for opening tickets. This information is collected in order to maintain service functionality and is not available to the public. Your data can be deleted by emailing `contact@letstalkpossibility.com`.\n\n**Terms of Service**: There is no current TOS. Please read our Privacy Policy to learn about what information we collect. At the moment, service will not be removed or revoked from any users for any reason, this is subject to change at any time. You consent to any changes when you use our service."
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
	await bot.add_cog(info(bot))