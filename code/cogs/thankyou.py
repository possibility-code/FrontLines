import discord
from discord.ext import commands
from discord import app_commands
import datetime
from views.reasons_view import view_reasons

class thankyou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    @app_commands.describe(user="User you would like to thank.")
    @app_commands.describe(reason="Optional reason for thanking the user.")
    async def thankyou(self, interaction: discord.Interaction, user: discord.User, *, reason: str = None):
        """Thank a user for something. Optionally provide a reason."""
        # Pull the latest thank you from the database that was sent by the same user and to the same user
        # If the thank you was sent less than 24 hours ago, don't let the user send another one
        latest_thankyou = self.bot.thanksdb.execute("SELECT * FROM thankyou WHERE user_id = ? AND thanked_user_id = ? ORDER BY timestamp DESC LIMIT 1", (interaction.user.id, user.id))
        latest_thankyou = latest_thankyou.fetchone()
        if latest_thankyou:
            thank_time = datetime.datetime.strptime(latest_thankyou[3], "%Y-%m-%d %H:%M:%S.%f")
            if datetime.datetime.now() - thank_time < datetime.timedelta(hours=24):
                return await interaction.response.send_message("You can only thank the same user once within 24 hours.", ephemeral=True)

        else:
            self.bot.thanksdb.execute("INSERT INTO thankyou VALUES (?,?,?,?)", (interaction.user.id, user.id, reason, datetime.datetime.now()))
            self.bot.thanksdb.commit()

            await interaction.response.send_message(f"You have thanked {user.mention}!", ephemeral=True)


    @app_commands.command()
    @app_commands.describe(user="The user whose profile you would like to see.")
    async def profile(self, interaction: discord.Interaction, user: discord.User):
        """See a users profile that contains all of their thank yous."""
        thank_yous = self.bot.thanksdb.execute("SELECT * FROM thankyou WHERE thanked_user_id = ?", (user.id,))
        thank_yous = thank_yous.fetchall()

        with_reasons = []

        for thank_you in thank_yous:
            if thank_you[2] != None:
                with_reasons.append(thank_you)

        embed = discord.Embed(
            description=f"{user.mention} has recieved ` {len(thank_yous)} ` thank yous, and ` {len(with_reasons)} ` have reasons.",
        )
        embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar.url)

        view = view_reasons(self.bot, interaction, with_reasons, user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
	await bot.add_cog(thankyou(bot))