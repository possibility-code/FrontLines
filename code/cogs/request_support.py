import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from reader import SUPPORT_CHANNEL

class request_support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    """
    Allow users to request support with the bot from a member of the Possibility Support Team.

    Here we are just confirming their decision and then adding them to the support queue.
    """
    @app_commands.command()
    @app_commands.default_permissions()
    @app_commands.checks.has_permissions(administrator=True)
    async def requestsupport(self, interaction: discord.Interaction):
        """Get help with the bot from a member of the Possibility Support Team. Server owners ONLY."""
        if interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title="Invalid Permissions",
                description="The only person that can use this command is the server owner.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        guild = interaction.guild
        owner = guild.owner

        # Confirm that the user wants to request support from the support team
        embed = discord.Embed(
            title="Request Confirmation",
            description="Are you sure you want to request support from the Possibility Support Team? If you are, please reply to this message with `yes` within the next 30 seconds.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

        a = ["y", "yes", "Yes", "YEs", "YES"]
        # Wait for the user to reply with 'yes'
        try:
            msg = await self.bot.wait_for('message', check=lambda message:message.author == interaction.user and message.channel.id == interaction.channel.id, timeout=30)
        # If the user doesn't reply within 30 seconds, cancel the setup, and send a message alerting the user
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Request Confirmation Timed Out",
                description="The request confirmation has timed out. If you would like to still request support with the bot, please rerun the `/requestsupport` command again.",
                color=discord.Color.red()
            )
            # Try to edit the message
            try:
                return await interaction.edit_original_response(embed=embed)
            # If the message was deleted, we get 'Not Found' so just return in order to cancel the setup overwrite
            except discord.errors.NotFound:
                return
        # If the user gave a valid 'yes' response, alert the user that their info is being
        # delted, and then return delete the info
        if msg.content in a:
            embed = discord.Embed(
                title="Request Confirmed",
                description="You request for support with the bot has been confirmed. Your ticket has been added to the queue, and a member of the support team will join your server and get in contact with you as soon as possible.",
            )
            await interaction.followup.send(embed=embed)

            self.bot.support_queue.append(owner.id)
            self.bot.support_info[owner.id] = {
                "guild_id": guild.id,
                "vol_id": None,
                "channel_id": None,
            }

            supp_channel = self.bot.get_channel(SUPPORT_CHANNEL)
            msg = await supp_channel.send("@everyone")
            await asyncio.sleep(0.5)
            await msg.delete()

            self.bot.tempdb.execute("INSERT INTO supporttemp VALUES (?,?)", (owner.id, 0))
            self.bot.tempdb.commit()
        # Else, the user didn't give a valid 'yes' response, so return alert the user that the setup overwrite was cancelled
        else:
            embed = discord.Embed(
                title = "Request Cancelled", 
                description = f"Your request for support has been cancelled as a valid 'yes' response was not sent.",
                color = discord.Color.orange()
            )
            return await interaction.followup.send(embed=embed)


async def setup(bot):
	await bot.add_cog(request_support(bot))