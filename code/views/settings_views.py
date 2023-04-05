import discord
import datetime

"""
Allow FrontLines staff to enable or disable the queue so that users can't
open anymore new tickets
"""
class settings_view_enabled(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Click to Disable Queue', style=discord.ButtonStyle.red, row=1)
    async def disable_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.queue_status = "disabled"
        embed = discord.Embed(
            title="Possbility ♾️ Frontlines"
        )
        embed.add_field(name="Queue", value=f"```Disabled```")
        embed.set_footer(text=f"FrontLines Settings | Last changed: {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

        view = settings_view_disabled(self.bot)
        await interaction.message.edit(embed=embed, view=view)
        await interaction.response.defer()

class settings_view_disabled(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Click to Enable Queue', style=discord.ButtonStyle.green, row=1)
    async def enable_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.queue_status = "enabled"
        embed = discord.Embed(
            title="Possbility ♾️ Frontlines"
        )
        embed.add_field(name="Queue", value=f"```Enabled```")
        embed.set_footer(text=f"FrontLines Settings | Last changed: {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

        view = settings_view_enabled(self.bot)
        await interaction.message.edit(embed=embed, view=view)
        await interaction.response.defer()