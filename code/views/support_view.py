import discord
from ticket_work.close_support import button_close_ticket

class support_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    # When the button is clicked, run the 'claim_ticket' function to attempt to connect the volunteer
    # to a user
    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.red, row=1)
    async def close_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await button_close_ticket(self.bot, interaction)