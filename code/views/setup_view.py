import discord
from ticket_work.open_ticket import open_ticket

"""
This button allows users to actually open a ticket, timeout MUST be None
"""
class setup_view(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Volunteer For Possibility ♾️", url='https://discord.gg/ffv2VGB', row=2))

    @discord.ui.button(label='Get Connected ', style=discord.ButtonStyle.blurple, row=1)
    async def get_connected(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_ticket(self.bot, interaction)