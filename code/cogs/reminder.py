import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Literal
import datetime
import pytz
import arrow

"""
Allow users to set their timezone and make reminders for themselves
"""
class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_load(self):
        self.reminder_loop.start()


    @app_commands.command()
    @app_commands.describe(timezone="What is your time zone? Choose UTC if yours is not listed.")
    async def timezoneset(self, interaction: discord.Interaction, timezone: Literal['Eastern', 'Central', 'Mountain', 'Pacific', 'Alaska', 'Hawaii', 'UTC']):
        """Set your time zone"""
        time = self.bot.remdb.execute("SELECT * FROM timezone WHERE user_id = ?", (interaction.user.id,))
        if time.fetchone() is None:
            self.bot.remdb.execute("INSERT INTO timezone VALUES (?,?)", (interaction.user.id, timezone))
            self.bot.remdb.commit()
            await interaction.response.send_message("Time zone set!", ephemeral=True)

        else:
            self.bot.remdb.execute("UPDATE timezone SET timezone = ? WHERE user_id = ?", (timezone, interaction.user.id))
            self.bot.remdb.commit()
            await interaction.response.send_message("Time zone updated!", ephemeral=True)


    @app_commands.command()
    @app_commands.describe(recur="Do you want this reminder to be sent evey day?")
    @app_commands.describe(time="Time for the reminder to be sent. Format: HH:MM (12 hour format)")
    @app_commands.describe(daytime="AM or PM")
    @app_commands.describe(message="Your actual reminder.")
    async def remind(
        self,
        interaction: discord.Interaction,
        recur: Literal['Yes', 'No'],
        time: str,
        daytime: Literal['AM', 'PM'],
        message: str):
        """Set a reminder for yourself"""
        zone = self.bot.remdb.execute("SELECT * FROM timezone WHERE user_id = ?", (interaction.user.id,))
        if zone.fetchone() is None:
            return await interaction.response.send_message("Please run the `/timezoneset` command in order to set your time zone. This is used so that the bot knows what time to send your reminders at.", ephemeral=True)

        else:
            # Make sure that `time` is in the correct format of HH:MM
            try:
                if time.split(':')[0].isdigit() and time.split(':')[1].isdigit():
                    if int(time.split(':')[0]) <= 12 or int(time.split(':')[1]) <= 59:
                        # Remove leading 0s from the time
                        if time.split(':')[0].startswith('0'):
                            time = time.split(':')[0].replace('0', '') + ':' + time.split(':')[1]
                        if daytime == 'AM':
                            if int(time.split(':')[0]) == 12:
                                new_time = time.split(':')[0].replace(str(int(time.split(':')[0])), '00') + ':' + time.split(':')[1]
                            else:
                                new_time = time

                        if daytime == 'PM':
                            if int(time.split(':')[0]) != 12:
                                new_time = time.split(':')[0].replace(str(int(time.split(':')[0])), str(int(time.split(':')[0]) + 12)) + ':' + time.split(':')[1]
                            else:
                                new_time = time

                        # If `new_time` still has a single digit hour (i.e. 1:00 PM), add a 0 to the front
                        if len(new_time.split(':')[0]) == 1:
                            new_time = '0' + new_time

                        # Get the user's time zone, and convert the time to UTC
                        timezone = self.bot.remdb.execute("SELECT timezone FROM timezone WHERE user_id = ?", (interaction.user.id,))
                        timezone = timezone.fetchone()[0]
                        if timezone != 'UTC':
                            timezone = pytz.timezone(f'US/{timezone}')
                            # Get the current UTC shift from the user's time zone
                            utc_shift = datetime.datetime.now(timezone).strftime('%z')
                            new_time_utc = arrow.get(new_time, 'HH:mm').shift(hours=-int(utc_shift[:3]), minutes=-int(utc_shift[3:]))
                        else:
                            new_time_utc = arrow.get(new_time, 'HH:mm')

                        self.bot.remdb.execute("INSERT INTO reminders VALUES (?,?,?,?)", (interaction.user.id, recur, new_time_utc.format('HH:mm'), message))
                        self.bot.remdb.commit()

                        await interaction.response.send_message(f"Your reminder has been set for {time} {daytime}", ephemeral=True)

                    else:
                        return await interaction.response.send_message("Invalid time format. Please use HH:MM")
                else:
                    return await interaction.response.send_message("Invalid time format. Please use HH:MM")
            except IndexError:
                return await interaction.response.send_message("Invalid time format. Please use HH:MM")


    @tasks.loop(seconds=60)
    async def reminder_loop(self):
        time = arrow.utcnow().format('HH:mm')
        reminders = self.bot.remdb.execute("SELECT * FROM reminders WHERE recur_time = ?", (time,))
        for reminder in reminders.fetchall():
            user = await self.bot.fetch_user(reminder[0])
            embed = discord.Embed(
                title="Reminder",
                description=reminder[3],
            )
            try:
                if reminder[1] == 'Yes':
                    await user.send(embed=embed)
                else:
                    await user.send(embed=embed)
                    self.bot.remdb.execute("DELETE FROM reminders WHERE user_id = ? AND message = ? AND recur_time = ?", (reminder[0], reminder[3], time))
                    self.bot.remdb.commit()
            except discord.errors.Forbidden:
                pass

async def setup(bot):
	await bot.add_cog(reminder(bot))