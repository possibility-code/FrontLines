import discord
import asyncio
import random

"""
We are not keeping transcripts or really any informatio regarding the support tickets,
so all that really must be done is to delete the channel and remove the user from the dicts/lists
"""
class confirm_close(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # If the user clicks 'Confirm' then run the close_ticket function
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.red, row=1)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await close_ticket(self.bot, interaction)


"""
Kept in this function in case in the future we decide to add more like a reason for closing the ticket
"""
async def button_close_ticket(bot, interaction):
    embed = discord.Embed(
        title="Ticket Closure",
        description="Are you sure you would like to close this ticket? If so, please click the button below.",
    )
    view = confirm_close(bot)
    await interaction.response.send_message(embed=embed, view=view)

"""
Logic to actually close the ticket and remove all of the temporary data
"""
async def close_ticket(bot, interaction):
    embed = discord.Embed(
        title="Ticket Closing",
        description="Thank you for helping another user. This ticket will close in 5 seconds.",
        color=discord.Color.green()
    )
    await interaction.response.edit_message(embed=embed, view=None)
    # Sleep for 5 seconds
    await asyncio.sleep(5)

    user_id = bot.support_channel_to_user[interaction.channel.id]
    user = bot.get_user(user_id)
    guild_id = bot.support_info[user_id]["guild_id"]

    # Send the user a message alerting them that their ticket has been closed
    embed = discord.Embed(
        title="Ticket Has Been Closed",
        description="We hope that your issue has been resolved. If you have any further questions, please feel free to open another ticket.",
    )
    await user.send(embed=embed)

    await interaction.channel.delete()

    # Delete the temp data from the supporttemp table
    bot.tempdb.execute("DELETE FROM supporttemp WHERE user_id = ?", (user_id,))
    bot.tempdb.commit()

    # Attempt to delete the temp data from ALL dicts/lists no matter what
    try:
        bot.support_queue.remove(user_id)
    except ValueError:
        pass
    try:
        del bot.support_channel_to_user[interaction.channel.id]
    except KeyError:
        pass
    try:
        del bot.support_info[user_id]
    except KeyError:
        pass