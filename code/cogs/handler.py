import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
import datetime

class slash_handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_error


    async def on_error(self, interaction: discord.Interaction, error):
        error = getattr(error, 'original', error)
        # If the error is a 'MissingPermissions' error, send the embed
        if isinstance(error, discord.errors.Forbidden):
            embed = discord.Embed(
                title = "→ Missing Permissions!",
                description = f"I am missing permissions in order to perform that task. Please make sure that you have invited me with the proper permissions enabled. In order to properly function, I require the following permissions:\n\n- Manage Roles\n- Manage Channels\n- Send Messages\n- Embed Links\n- Attach Files\n\nPlease remove me from this server, and reinvite me with [this invite link]( https://discord.com/oauth2/authorize?client_id=982806583060885525&permissions=268487696&scope=bot%20applications.commands), then re-run the command.\n\nIf you believe this is a mistake, please message the developer Fiji#3608.",
                colour = discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(error, CommandNotFound):
            return
        # Else, we have a new error, so print the error to the console and write it to error.log
        else:
            print(error)
            with open("error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: {error}\n")


async def setup(bot: commands.Bot):
    await bot.add_cog(slash_handlers(bot))