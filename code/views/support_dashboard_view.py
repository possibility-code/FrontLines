import discord
from ticket_work.claim_support import claim_support

"""
Allows volunteers to claim a users ticket, timeout MUST be None
"""
class support_dashboard_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Connect With User', style=discord.ButtonStyle.green, row=1)
    async def connect_with_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await claim_support(self.bot, interaction)