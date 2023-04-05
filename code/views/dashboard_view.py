import discord
from ticket_work.claim_ticket import claim_ticket

"""
Allow volunteers to connect with users

MUST have no timeout
"""
class dashboard_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Connect With User', style=discord.ButtonStyle.green, row=1)
    async def connect_with_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await claim_ticket(self.bot, interaction)