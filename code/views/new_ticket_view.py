import discord
from views.transfer_or_close_view import transfer_or_close_view
from views.ticket_pager_view import ticket_pager_view

"""
Sent at the beginning of a ticket when it is opened

MUST have no timeout
"""
class new_ticket_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Ticket Status', style=discord.ButtonStyle.blurple, row=1)
    async def ticket_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Ticket Status",
            description=f":one:` Transfer Ticket `\n\n:two:` Close ` ",
        )
        view = transfer_or_close_view(self.bot)
        await interaction.response.send_message(embed=embed, view=view)


    # NOTE: Part of Keegan's plan to add this in the future

    # @discord.ui.button(label='Ticket Pager', style=discord.ButtonStyle.blurple, row=1)
    # async def ticket_pager(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     embed = discord.Embed(
    #         title="Ticket Pager",
    #         description=f":one:` Purple `\n\n:two:` Blue `\n\n:three:` Orange `\n\n:four:` On Call `",
    #     )
    #     view = ticket_pager_view(self.bot)
    #     await interaction.response.send_message(embed=embed, view=view)