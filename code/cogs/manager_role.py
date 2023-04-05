import discord
from discord.ext import commands
from discord import app_commands
import asyncpg

"""
Manager roles are able to view ALL tickets without actually being assigned to them.
You can add and remove manager roles using the commands below, but the commands
are only available to the 2 servers defined below and only to admins.
"""
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(573919902042423317), discord.Object(977410826233344040))
class manager_role(commands.GroupCog, name="managerrole"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot


    # Command so that Keegan or another admin can add manager roles to the main server
    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="Manager role that you would like to add to the database")
    async def add(self, interaction: discord.Interaction, role: discord.Role):
        """Add a manager role to the database"""
        # Insert the manager role into the database and send a message to the user
        try:
            await self.bot.db.execute("INSERT INTO manager_roles VALUES ($1,$2)", interaction.guild.id, role.id)

            embed = discord.Embed(
                title="Manager Role Added",
                description=f"{role.mention} has been added as a manager role.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        # If the role is already in the database, we get 'UniqueViolation', so alert the user
        except asyncpg.exceptions.UniqueViolationError:
            embed = discord.Embed(
                title="Manager Role Already Added",
                description=f"{role.mention} is already a manager role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    # Command so that Keegan or another admin can remove manager roles to the main server
    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="Manager role that you would like to remove from the database")
    async def remove(self, interaction: discord.Interaction, role: discord.Role):
        """Remove a manager role from the database"""
        # Delete from the database and send a message to the user
        await self.bot.db.execute("DELETE FROM manager_roles WHERE guild_id = $1 and role_id = $2", interaction.guild.id, role.id)

        embed = discord.Embed(
            title="Manager Role Removed",
            description=f"{role.mention} has been removed as a manager role.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(manager_role(bot))