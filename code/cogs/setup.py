import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncpg
from views.setup_view import setup_view
import asyncio


class setup_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(category_name="Name for the new category that will be created")
    @app_commands.describe(channel_name="Name for the new channel that will be created")
    @app_commands.describe(role="Role of the members in your server. This role will be used to determine who can open tickets")
    async def setup(self, interaction: discord.Interaction, category_name: str, channel_name: str, role: discord.Role):
        """Setup your server for the ticket system"""
        # Make sure the guild doesnt already have a setup channel/message in the server
        if len(channel_name) > 100:
            embed = discord.Embed(
                title="Channel Name Too Long",
                description="The channel name you provided is too long. Please provide a channel name that is less than 100 characters.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        async with self.bot.db.acquire() as conn:
            data = await conn.fetchval("SELECT guild_id FROM server_info WHERE guild_id = $1", interaction.guild.id)
            if data:
                # If they already have a setup stored, ask them if they want to overwrite it
                embed = discord.Embed(
                    title="Server Already Setup",
                    description="My database shows that this server has already been setup. If the setup was incorrect, or the message/channel/category is no longer there, and you would like to overwrite your previous data, please reply to this message with `yes` within the next 30 seconds and then run the `/setup` command again.",
                    color = discord.Color.red()
                )
                await interaction.response.send_message(embed=embed)

                a = ["y", "yes", "Yes", "YEs", "YES"] # Create a list of valid 'yes' responses
                # Wait for the user to reply with 'yes'
                try:
                    msg = await self.bot.wait_for('message', check=lambda message:message.author == interaction.user and message.channel.id == interaction.channel.id, timeout=30)
                # If the user doesn't reply within 30 seconds, cancel the setup, and send a message alerting the user
                except asyncio.TimeoutError:
                    embed = discord.Embed(
                        title="Setup Overwrite Timed Out",
                        description="The setup overwrite has timed out. If you would like to overwrite your previous setup, please rerun the `/setup` command.",
                        color=discord.Color.red()
                    )
                    # Try to edit the message
                    try:
                        return await interaction.edit_original_response(embed=embed)
                    # If the message was deleted, we get 'Not Found' so just return in order to cancel the setup overwrite
                    except discord.errors.NotFound:
                        return
                # If the user gave a valid 'yes' response, alert the user that their info is being
                # delted, and then return delete the info
                if msg.content in a:
                    embed = discord.Embed(
                        title="Previous Setup Overwritten",
                        description="Your previous setup has been overwritten, please run the `/setup` command again to setup your server.",
                    )
                    await interaction.followup.send(embed=embed)
                    return await self.bot.db.execute("DELETE FROM server_info WHERE guild_id = $1", interaction.guild.id)
                # Else, the user didn't give a valid 'yes' response, so return alert the user that the setup overwrite was cancelled
                else:
                    embed = discord.Embed(
                        title = "Overwrite Cancelled", 
                        description = f"Your previous setup has not been overwritten.",
                        color = discord.Color.orange()
                    )
                    return await interaction.followup.send(embed=embed)

        # Else, if they don't have a setup stored, create a new one
        # Create a new category, channel, and then set the permission to the channel 
        # so that the role given by the author can view the channel, but not send messages
        category = await interaction.channel.guild.create_category_channel(category_name)
        channel = await interaction.channel.guild.create_text_channel(channel_name, category=category, topic="Are you in a crisis? Call 800-273-8255 or Text POSSIBILITY to 741741 | <:space_heart:977673187255021599> Are you having a bad day? Click \"Get Connected\" below")
        try:
            await channel.set_permissions(role, read_messages=True, send_messages=False)
            await channel.set_permissions(self.bot.user, read_messages=True, send_messages=True)
        except:
            with open("error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: SetupChannelPermissionErrro\n")
            pass

        wait_time = self.bot.avg_wait

        # Create the embed for the new channel. This message will give information to users
        # and then we add the view 'setup_view' to the message so that users can open tickets

        embed = discord.Embed(
            title="Possibility ♾️ Frontlines",
            description=f"We are excited to walk with you in your mental health journey, to provide you the space where you feel heard, and give you the ability to express yourself at your own pace. Our volunteers, however, aren't professionals; instead, they are ordinary people. To create a more relatable environment, and as we are operating our support department of only volunteers, we cannot keep a 24/7 service. Instead, our operating hours are purely based on active staffing.\n\nIf you want to connect with a support volunteer, all you have to do is click `Get Connected` at the bottom of this message. After opening the ticket, a pop-up will appear which will ask you a few questions, this is to help us provide you with the best support. Then you we will open a thread in this channel, which only you can view, and you will be connected to the next available volunteer in the Possibility server.\n\n**UNDERSTAND THAT WE ARE NOT A CRISIS LINE. IF YOU ARE IN A CRISIS, WE WILL HELP DIRECT YOU TO LOCAL RESOURCES**\n\n**More Information**\n` {wait_time} ` Average wait time\n\n` {len(self.bot.online_volunteers)} ` Online Volunteers\n\n*Data last updated on ` {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC `*",
            color=0x0079FF
        )
        # Try to add the view, send the message, and then add all of the data to the database
        try:
            view = setup_view(self.bot)
            message = await channel.send(embed=embed, view=view)
            await self.bot.db.execute("INSERT INTO server_info (guild_id, message_id, channel_id, everyone_role) VALUES ($1,$2,$3,$4)", interaction.guild.id, message.id, channel.id, role.id)
        # If for some reason the checks at the top didn't work to stop this error, this is added, just return
        except asyncpg.exceptions.UniqueViolationError:
            return
        # If everything worked, and a new setup was created, alert the user through an ephemeral message
        # that the setup process was a success
        await interaction.response.send_message(f"Success! Setup has been completed, users can now open tickets in {channel.mention}.", ephemeral=True)


async def setup(bot):
	await bot.add_cog(setup_command(bot))