import discord
from discord.ext import commands
from discord import app_commands
from views.waiver_view import sign_waiver_view

class waiver(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot


    # Command to allow users to sign the required waiver
    @app_commands.command()
    async def waiver(self, interaction: discord.Interaction):
        """Sign this waiver in order to have the ability to open tickets"""
        # Create the embed that gives them the basic first page of the waiver
        embed = discord.Embed(
            title = "WAIVER",
            description = f"we are not a 24/7 service. Instead, our operation hours are determined by staffing and availability. If volunteers are working, we are working; this does not mean we will be able to get to you instantly. Although we will always try to keep our times low, it's not our primary goal. Instead, our goal is to provide a meaningful impact on your life.\n\nWe are not a crisis service, and in the event of a crisis, out job is to help guide our members to local crisis support.\n\nYour support sessions can be terminated for making volunteers feel uncomfortable, or for breaking Discord ToS. We also will keep a transcript of the messages sent in the ticket.\n\nAt the bottom of this message is a button named `Sign Waiver`. Clicking this button acknowledges that you have read this waiver and gives us the ability to help you find resources or a place for you to express yourself. After clicking this button, this message will be edited and you will be required to answer 1 question before you can open a ticket.",
            color = 0x0079FF
        )
        view = sign_waiver_view(self.bot)
        # Try to send the embed to the user, if it works, a success ephemeral follows
        try:
            await interaction.user.send(embed=embed, view=view)
            await interaction.response.send_message("Success, check your DMs for the waiver.", ephemeral=True)
        # If the users DMs are closed we get 'Forbidden', so send an ephemeral alerting the user
        except discord.Forbidden:
            embed = discord.Embed(
                title = "DMs Not Open!",
                description = "Your DMs are closed. Please open them and try again.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
	await bot.add_cog(waiver(bot))