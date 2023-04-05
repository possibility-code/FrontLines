import discord
import math

class timeout_edit:
    def __init__(self, bot):
        self.bot = bot

    async def edit_message(self, interaction):
        embed = discord.Embed(
            title="Message Timed Out!",
            description="You can no longer look at this user's thank yous as the message timed out. Please re-run the `/profile` command if you would like to continue viewing their thank yous.",
            color=discord.Color.red()
        )
        await interaction.edit_original_response(embed=embed, view=None)

"""
Load x page of the user's thank yous and return the embed with the information
"""
async def load_page(self, with_reasons, user, page: int):
        items_per_page = 5
        pages = math.ceil(len(with_reasons) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page

        embed = discord.Embed(
            description=f"Reasons why {user.name}'s been thanked."
        )
        embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar.url)

        for reason in enumerate(with_reasons[start:end], start=start):
            try:
                user = self.bot.get_user(reason[1][0])
                name = user.name
            except:
                name = "Unknown"

            embed.add_field(name=f"{name} ({reason[1][1]})", value=f'"{reason[1][2]}"', inline=False)

        embed.set_footer(text=f"Page {page}/{pages} | {len(self.with_reasons)}" + " total reasons" if len(self.with_reasons) > 1 else " total reason")

        return embed

"""
Allow users to optionally view the reasons why the user has been thanked
"""
class view_reasons(discord.ui.View):
    def __init__(self, bot, interaction, with_reasons, user):
        super().__init__(timeout=45)
        self.bot = bot
        self.interaction = interaction
        self.with_reasons = with_reasons
        self.user = user
        self.timeout_edit = timeout_edit(bot)

    async def on_timeout(self) -> None:
        await self.timeout_edit.edit_message(self.interaction)

    @discord.ui.button(label='View Reasons', style=discord.ButtonStyle.gray, row=1)
    async def view_reasons(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await load_page(self, self.with_reasons, self.user, 1)

        await self.interaction.edit_original_response(embed=embed, view=change_reasons_pages(self.bot, self.interaction, self.with_reasons, self.user, 1))
        await interaction.response.defer(ephemeral=True)

"""
Allow users to go to next and previous pages of the user's thank yous
"""
class change_reasons_pages(discord.ui.View):
    def __init__(self, bot, interaction, with_reasons, user, page: int):
        super().__init__(timeout=120)
        self.timeout_edit = timeout_edit(bot)
        self.with_reasons = with_reasons
        self.interaction = interaction
        self.bot = bot
        self.user = user
        self.page = page

    async def on_timeout(self) -> None:
        await self.timeout_edit.edit_message(self.interaction)

    @discord.ui.button(label='Previous Page', style=discord.ButtonStyle.gray, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await load_page(self, self.with_reasons, self.user, self.page - 1)

        await self.interaction.edit_original_response(embed=embed, view=change_reasons_pages(self.bot, self.interaction, self.with_reasons, self.user, self.page - 1))
        await interaction.response.defer(ephemeral=True)

    @discord.ui.button(label='Next Page', style=discord.ButtonStyle.gray, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await load_page(self, self.with_reasons, self.user, self.page + 1)

        await self.interaction.edit_original_response(embed=embed, view=change_reasons_pages(self.bot, self.interaction, self.with_reasons, self.user, self.page + 1))
        await interaction.response.defer(ephemeral=True)