import discord
from ticket_work.gpt_rec import get_gpt_recommendation

"""
Get a recommendation on what to say to the user from Chat-GPT
"""
class gpt_rec_view(discord.ui.View):
    def __init__(self, messages):
        super().__init__(timeout=None)
        self.messages = messages

    @discord.ui.button(label='Get AI Recommendation', style=discord.ButtonStyle.gray, row=1)
    async def get_ai_rec(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Please wait while the AI generates a recommendation...",
            description="This may take a few seconds."
        )
        await interaction.response.send_message(embed=embed)
        await get_gpt_recommendation(self.messages, interaction)