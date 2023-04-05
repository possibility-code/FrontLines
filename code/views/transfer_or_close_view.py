import discord
from ticket_work.close_ticket import button_close_ticket
from ticket_work.transfer_ticket import transfer_ticket
from ticket_work.requeue_ticket import requeue_ticket
import asyncio
from reader import MAIN_SERVER
from ticket_work.close_ticket import button_close_ticket

"""
This is the view that is sent when a volunteer clicks the 'Ticket Status' and
'Transfer Ticket' buttons

They are now able to continue with the transfer, or cancel the transfer
"""
class id_yes_or_no_view(discord.ui.View):
    def __init__(self, bot, new_vol):
        super().__init__(timeout=None)
        self.bot = bot
        self.new_vol = new_vol

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green, row=1)
    async def confirm_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await transfer_ticket(self.bot, interaction, self.new_vol)
        return

    @discord.ui.button(label='No', style=discord.ButtonStyle.red, row=1)
    async def cancel_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Transfer Cancelled",
            description="The ticket transfer has been cancelled.",
        )
        await interaction.response.edit_message(embed=embed, view=None)

"""
If the volunteer chooses to requeue a ticket, this view is sent to confirm that
"""
class confirm_queue(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.red, row=1)
    async def confirm_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await requeue_ticket(self.bot, interaction)
        return 

"""
Users can either transfer the ticket to another volunteer, or send the ticket back to the queue
"""
class transfer_or_queue_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # If the Volunteer User ID button is clicked, prompt the user to reply with the user ID
    @discord.ui.button(label='1: Volunteer User ID', style=discord.ButtonStyle.blurple, row=1)
    async def volunteer_user_id(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Reply with the User ID",
            description=f"Please reply to this message with the user ID of the volunteer you want this ticket to be sent to. Please note, the user ID must be contained within `[]`, for example, `[455221909257453577]`",
        )
        await interaction.response.edit_message(embed=embed, view=None)
        # Wait for the user to send the user ID within brackets (e.g. [455221909257453577])
        try:
            msg = await self.bot.wait_for('message', check=lambda message:message.author == interaction.user and message.channel.id == interaction.channel.id, timeout=45)
        # If the user does not reply within 45 seconds, we edit the message to inform the user that they have timed out
        # But if the message was deleted, we get 'Not Found', so just return
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Transfer Timed Out",
                description="The ticket transfer has timed out. If you would still like to transfer this ticket, please try again.",
            )
            try:
                return await interaction.edit_original_response(embed=embed, view=None)
            except discord.errors.NotFound:
                return
        # If the message was sent within brackets (e.g. [455221909257453577]), we continue
        if msg.content.startswith('[') and msg.content.endswith(']'):
            vol_id = msg.content[1:-1]
            main_server = self.bot.get_guild(MAIN_SERVER)
            user = main_server.get_member(int(vol_id))
            # If the user is the same as the current volunteer
            if user.id == interaction.user.id:
                embed = discord.Embed(
                    title="Transfer Cancelled",
                    description="You cannot transfer a ticket to yourself, try again with a new volunteer ID.",
                    color=discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            # If the ID is valid
            if user != None:
                embed = discord.Embed(
                    title="Confirm Transfer",
                    description=f"Would you like me to transfer the ticket to {user.mention}?",
                )
                view = id_yes_or_no_view(self.bot, user)
                await interaction.edit_original_response(embed=embed, view=view)
            # Else, ID was not valid
            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description="The user ID you provided was not found in the server. Please try again.",
                    color = discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
        # If the message was not sent within brackets
        else:
            embed = discord.Embed(
                title="Ticket Transfer Cancelled",
                description="You did not provide a volunteer ID within `[]`. If you would still like to transfer the ticket, please try again.",
                color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)

    # If the user clicks the 'Send to Queue' button, we edit the message to show a confirmation
    # message, and set the view to show a confirm button
    @discord.ui.button(label='2: Send to Queue', style=discord.ButtonStyle.blurple, row=1)
    async def send_to_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Confirm Ticket Sending",
            description=f"Press the `Confirm` button below to send the ticket back to the queue.",
        )
        view = confirm_queue(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

"""
Allow the volunteer to either transfer or close the ticket, transfering the ticket
has 2 possible options
"""
class transfer_or_close_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='1: Transfer', style=discord.ButtonStyle.blurple, row=1)
    async def transfer_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Ticket Transfer",
            description=f":one:` Volunteer User ID `\n\n:two:` Send to Queue `",
        )
        view = transfer_or_queue_view(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label='2: Close', style=discord.ButtonStyle.blurple, row=1)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await button_close_ticket(self.bot, interaction)