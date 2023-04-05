import discord
import asyncpg

"""
Add or update the user's consent in the database, then send confirmation message
"""
async def add(bot, interaction, save_message):
    try:
        await bot.db.execute("INSERT INTO consent (user_id, waiver, save_consent) VALUES ($1,$2,$3)", interaction.user.id, 'Signed', save_message)
    except asyncpg.exceptions.UniqueViolationError:
        await bot.db.execute("UPDATE consent SET save_consent = $1 WHERE user_id = $2", save_message, interaction.user.id)

    embed = discord.Embed(
        title = "Waiver and Consent Form",
        description = f"You have completed the waiver and consent form, thank you. You may now open tickets by clicking the \"Get Connected\" button. Your responses are shown below.\n\nWaiver: Signed\nMessage Saving: {save_message}",
        color = discord.Color.green()
    )
    await interaction.response.edit_message(embed=embed, view=None)


class timeout_edit:
    def __init__(self, bot):
        self.bot = bot

    async def edit_message(self, interaction):
        embed = discord.Embed(
            title="Message Timed Out!",
            description="You did not finish the waiver in time and your message has timed out. You can restart the process by running the `/waiver` command.",
            color=discord.Color.red()
        )
        await interaction.edit_original_response(embed=embed, view=None)

"""
Apply the "Sign Waiver" button to the embed, when clicked
send the user to the next question
"""
class sign_waiver_view(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.timeout_edit = timeout_edit(bot)

    @discord.ui.button(label='Sign Waiver', style=discord.ButtonStyle.green, row=1)
    async def sign_waiver(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title = "Question 1: Message Saving",
            description = f"We use your messages in the context of your ticket in order to keep transcripts of your tickets for storage purposes. Only users with the proper authentication are able to view this content.\n\nPlease note, choosing `no` does not mean you will not be able to open tickets, and your decision can be changed by re-running the `/waiver` command and answering differently.",
            color = 0x0079FF
        )
        view = save_view(self.bot, interaction)
        await interaction.response.edit_message(embed=embed, view=view)

"""
Whether or not the user wants their messages saved
Either way their response is ultimately saved in the database
"""
class save_view(discord.ui.View):
    def __init__(self, bot, interaction):
        super().__init__(timeout=180)
        self.bot = bot
        self.interaction = interaction
        self.timeout_edit = timeout_edit(bot)

    async def on_timeout(self) -> None:
        await self.timeout_edit.edit_message(self.interaction)

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green, row=1)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await add(self.bot, interaction, 'Yes')

    @discord.ui.button(label='No', style=discord.ButtonStyle.red, row=1)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await add(self.bot, interaction, 'No')