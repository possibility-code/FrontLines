import discord

"""
NOTE: Keegan apparently has plans for the pager function in the future, however,
it is not yet implemented. These are just placedholders at the moment.
"""
class ticket_pager_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(emoji='1️⃣', style=discord.ButtonStyle.grey, row=1)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="",
            description=f"",
        )
        view = (self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(emoji='2️⃣', style=discord.ButtonStyle.grey, row=1)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="",
            description=f"",
        )
        view = (self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(emoji='3️⃣', style=discord.ButtonStyle.grey, row=1)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="",
            description=f"",
        )
        view = (self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(emoji='4️⃣', style=discord.ButtonStyle.grey, row=1)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="",
            description=f"",
        )
        view = (self.bot)
        await interaction.response.edit_message(embed=embed, view=view)