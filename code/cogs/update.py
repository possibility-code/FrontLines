import discord
from discord.ext import commands
import datetime
from reader import MAIN_SERVER, DASHBOARD_CHANNEL, STATISTICS_CHANNEL, SETTINGS_CHANNEL, SUPPORT_CHANNEL
from discord.ext import tasks
from cogs.setup import setup_view
from views.dashboard_view import dashboard_view
import asyncpg
from views.settings_views import settings_view_disabled, settings_view_enabled
from views.support_dashboard_view import support_dashboard_view
import asyncio
from ticket_work.vol_clocked_out import vol_has_clocked_out
import requests
import datetime

class updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_messages = [] # dashboard, support, category, statistics, settings

    async def cog_load(self):
        self.update_main_messages.start()
        self.update_setup_message.start()
        self.add_wait_time.start()
        self.get_clocked_in_users.start()
        self.check_for_vol_clock_out.start()
        self.check_for_afk_user.start()
        self.check_for_ticket_reopen.start()

    """
    Update all of the main messages from MAIN_SERVER, includes the dashboard, support,
    category, statistics, and settings messages, if they are not there to update (been deleted)
    then we will re-create them and add the data to the database
    """
    @tasks.loop(seconds=30)
    async def update_main_messages(self):
        await self.bot.wait_until_ready()

        main_server = self.bot.get_guild(MAIN_SERVER)

        dashboard_channel = main_server.get_channel(DASHBOARD_CHANNEL)
        support_channel = main_server.get_channel(SUPPORT_CHANNEL)
        statistics_channel = main_server.get_channel(STATISTICS_CHANNEL)
        settings_channel = main_server.get_channel(SETTINGS_CHANNEL)

        if len(self.update_messages) != 5:
            try:
                # Try to get the messages from the database
                # Get the message ids from the database and then get the messages
                async with self.bot.db.acquire() as conn:
                    messages = await conn.fetch("""SELECT
                        dashboard_message_id,
                        support_message_id,
                        category_message_id,
                        statistics_message_id,
                        settings_message_id
                    FROM main_messages""")
                    categories = await conn.fetch("SELECT category FROM ticket_info")
                    ticket_count = await conn.fetch("SELECT date FROM ticket_count")

                dashboard_message = await dashboard_channel.fetch_message(messages[0][0])
                support_message = await support_channel.fetch_message(messages[0][1])
                category_message = await statistics_channel.fetch_message(messages[0][2])
                statistics_message = await statistics_channel.fetch_message(messages[0][3])
                settings_message = await settings_channel.fetch_message(messages[0][4])
            # Except the message isn't found, or the data is not in the database
            except (discord.errors.NotFound, IndexError):
                # Purge any past messages that might be in the channels
                await dashboard_channel.purge(limit=5)
                await support_channel.purge(limit=5)
                await statistics_channel.purge(limit=5)
                await settings_channel.purge(limit=5)

                # Create the messages
                load_embed = discord.Embed(title="Loading...")
                dashboard_message = await dashboard_channel.send(embed=load_embed)
                support_message = await support_channel.send(embed=load_embed)
                category_message = await statistics_channel.send(embed=load_embed)
                statistics_message = await statistics_channel.send(embed=load_embed)
                settings_message = await settings_channel.send(embed=load_embed)

                # Add the messages to the database
                async with self.bot.db.acquire() as conn:
                    try:
                        await conn.execute("""INSERT INTO main_messages (
                            guild_id,
                            dashboard_message_id,
                            support_message_id,
                            category_message_id,
                            statistics_message_id,
                            settings_message_id
                        ) VALUES ($1, $2, $3, $4, $5, $6)""", MAIN_SERVER, dashboard_message.id, support_message.id, category_message.id, statistics_message.id, settings_message.id)
                    except asyncpg.exceptions.UniqueViolationError:
                        await conn.execute("""UPDATE main_messages SET
                            dashboard_message_id = $1,
                            support_message_id = $2,
                            category_message_id = $3,
                            statistics_message_id = $4,
                            settings_message_id = $5
                        WHERE guild_id = $6""", dashboard_message.id, support_message.id, category_message.id, statistics_message.id, settings_message.id, MAIN_SERVER)

            self.update_messages = [dashboard_message.id, support_message.id, category_message.id, statistics_message.id, settings_message.id]

        else:
            dashboard_message = dashboard_channel.get_partial_message(self.update_messages[0])
            support_message = support_channel.get_partial_message(self.update_messages[1])
            category_message = statistics_channel.get_partial_message(self.update_messages[2])
            statistics_message = statistics_channel.get_partial_message(self.update_messages[3])
            settings_message = settings_channel.get_partial_message(self.update_messages[4])

        async with self.bot.db.acquire() as conn:
            categories = await conn.fetch("SELECT category FROM ticket_info")
            ticket_count = await conn.fetch("SELECT date FROM ticket_count")
            active_guilds = await conn.fetch("SELECT guild_id FROM server_info")
        try:
            # DASHBOARD
            # Set the view to the 'dashboard_view' so that volunteers can connect with users
            embed = discord.Embed(
                title="Possbility ♾️ Frontlines"
            )
            embed.add_field(name="Active Tickets", value=f"```{len(self.bot.active_ticket)}```", inline=False)
            embed.add_field(name="Queued Tickets", value=f"```{len(self.bot.ticket_queue)}```", inline=False)
            embed.set_footer(text=f"Click below to connect to the next person in queue | Last updated on {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

            view = dashboard_view(self.bot)
            await dashboard_message.edit(embed=embed, view=view)

            # SUPPORT DASHBOARD
            # Set the view to the 'support_dashboard_view' so that volunteers can connect with users
            embed = discord.Embed (
                title="Possbility ♾️ Frontlines - Bot Support",
            )
            embed.add_field(name="Active Tickets", value=f"```{len(self.bot.support_active):,}```")
            embed.add_field(name="Queued Tickets", value=f"```{len(self.bot.support_queue):,}```")
            embed.set_footer(text=f"Click below to connect with the next person in queue | Last updated on {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

            view = support_dashboard_view(self.bot)
            await support_message.edit(embed=embed, view=view)

            #CATEGORIES
            # Create a dictionary of categories and their respective counts of repeats
            # (e.g. {'test_one': 15, 'test_two': 53})
            cat = {i:categories.count(i) for i in categories}

            embed = discord.Embed(
                title="Possbility ♾️ Frontlines",
                description="Below are the statistics for the top 10 issue categories that members have faced."
            )
            for entry in cat:
                embed.add_field(name=entry[0], value=f"```{cat[entry]} | {round(int(cat[entry])/len(categories)*100, 1)}%```", inline=True)
            embed.set_footer(text=f"FrontLines Statistics | Last Updated: {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

            await category_message.edit(embed=embed)

            #STATISTICS
            daily = 0
            weekly = 0
            total = 0
            last_week_day = datetime.date.today() - datetime.timedelta(days=7)
            # Get the date of all ticket entries, then add 1 to the variables
            # which apply to the ticket date e.g. a ticket from today will
            # add one to daily, weekly, and total but a ticket from yesterday
            # will only add one to weekly and total
            for date in ticket_count:
                date = date[0]
                if date == datetime.date.today():
                    daily += 1

                if date >= last_week_day and last_week_day <= date:
                    weekly += 1

                total += 1

            member_count = 0

            for guild in self.bot.guilds:
                member_count += guild.member_count

            embed = discord.Embed(
                title="Possibilty ♾️ Frontlines"
            )
            embed.add_field(name="**Guilds**", value = f"```{len(self.bot.guilds):,}```"),
            embed.add_field(name="**Active Guilds**", value = f"```{len(active_guilds):,}```", inline=True),
            embed.add_field(name="**Users**", value = f"```{member_count:,}```", inline=False),
            embed.add_field(name="**Tickets Today**", value=f"```{daily:,}```", inline=False),
            embed.add_field(name="**Tickets This Week**", value=f"```{weekly:,}```", inline=False),
            embed.add_field(name="**Total Tickets**", value=f"```{total:,}```", inline=False),
            embed.set_footer(text=f"FrontLines Statistics | Last Updated: {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")

            await statistics_message.edit(embed=embed)

            #SETTINGS
            embed = discord.Embed(
                title="Possbility ♾️ Frontlines"
            )
            embed.add_field(name="Queue", value=f"```{self.bot.queue_status}```")
            embed.set_footer(text=f"FrontLines Settings | Last changed: {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC")
            # Depending on the value of self.bot.queue_status, set the view to the correct view
            if self.bot.queue_status == "enabled":
                view = settings_view_enabled(self.bot)
            elif self.bot.queue_status == "disabled":
                view = settings_view_disabled(self.bot)

            await settings_message.edit(embed=embed, view=view)
        except discord.errors.NotFound:
            await self.bot.db.execute("DELETE FROM main_messages WHERE guild_id = $1", MAIN_SERVER)
            self.update_messages.clear()

    """
    Every hour, add the current wait time to the database
    This is used so that admins can see the average wait time over time
    """
    @tasks.loop(minutes=50)
    async def add_wait_time(self):
        await self.bot.wait_until_ready()
        # Get the current time
        cur_time = datetime.datetime.now()

        wait_time = str(self.bot.avg_wait)

        try:
            await self.bot.db.execute("INSERT INTO wait_time (date, hour, wait_time) VALUES ($1,$2,$3)", datetime.date.today(), cur_time.hour, wait_time)
        except asyncpg.exceptions.UniqueViolationError:
            return

    """
    Update the messages across all guilds that allow users to join the queue for
    support tickets
    """
    @tasks.loop(minutes=10)
    async def update_setup_message(self):
        await self.bot.wait_until_ready()
        # Select the guild_id, channel_id, and message_id for every server that a setup entry
        async with self.bot.db.acquire() as conn:
            data = await conn.fetch("SELECT guild_id, channel_id, message_id FROM server_info")

        # For each entry in data, get the guild, channel, and message
        for entry in data:
            await asyncio.sleep(1)
            guild_id, channel_id, message_id = entry

            server = self.bot.get_guild(guild_id)
            try:
                channel = server.get_channel(channel_id)
                message = channel.get_partial_message(message_id)
            # If the channel/message is deleted, just delete the server information from the database
            # the user will have to re-setup the server
            except AttributeError:
                return await self.bot.db.execute("DELETE FROM server_info WHERE guild_id = $1", guild_id)

            embed = discord.Embed(
                title="Possibility ♾️ Frontlines",
                description=f"We are excited to walk with you in your mental health journey, to provide you the space where you feel heard, and give you the ability to express yourself at your own pace. Our volunteers, however, aren't professionals; instead, they are ordinary people. To create a more relatable environment, and as we are operating our support department of only volunteers, we cannot keep a 24/7 service. Instead, our operating hours are purely based on active staffing.\n\nIf you want to connect with a support volunteer, all you have to do is click `Get Connected` at the bottom of this message. After opening the ticket, a pop-up will appear which will ask you a few questions, this is to help us provide you with the best support. Then you we will open a thread in this channel, which only you can view, and you will be connected to the next available volunteer in the Possibility server.\n\n**UNDERSTAND THAT WE ARE NOT A CRISIS LINE. IF YOU ARE IN A CRISIS, WE WILL HELP DIRECT YOU TO LOCAL RESOURCES**\n\n**More Information**\n` {self.bot.avg_wait} ` Average wait time\n\n` {len(self.bot.online_volunteers)} ` Online Volunteers\n\n*Data last updated on ` {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')} UTC `*",
                color=0x0079FF
            )
            view = setup_view(self.bot)
            await message.edit(embed=embed, view=view)

    """
    Pull the ids of the currently clocked in volunteers from the API
    """
    @tasks.loop(seconds=45)
    async def get_clocked_in_users(self):
        # Pull the data from the API and update the list of online volunteers
        data = requests.get("http://127.0.0.1:4200/clocked_in_users").json()

        self.bot.online_volunteers.clear()
        for entry in data:
            self.bot.online_volunteers.append(entry)


    @tasks.loop(seconds=60)
    async def check_for_vol_clock_out(self):
        # For every volunteer in the list of keys of 'active_ticket'
        for vol_id in list(self.bot.active_ticket.keys()):
            # If the volunteer ID is not in online_volunteer, that means they have clocked out
            if vol_id not in self.bot.online_volunteers:
                user_id = self.bot.active_ticket[vol_id]
                await vol_has_clocked_out(self.bot, vol_id, user_id)
            else:
                return


    @tasks.loop(minutes=2)
    async def check_for_afk_user(self):
        # For every user that has an entry in `bot.ticket_info`, get `last_message`
        for user_id in list(self.bot.ticket_info.keys()):
            if user_id not in self.bot.inactive_ticket:
                last_message = self.bot.ticket_info[user_id]['last_message']
                # If the user has been inactive for 2 hours, send the INACTIVE status message
                if last_message:
                    if datetime.datetime.now(datetime.timezone.utc) - last_message.created_at > datetime.timedelta(hours=2):
                        channel_id = self.bot.ticket_info[user_id]['channel_id']
                        print(channel_id)
                        channel = self.bot.get_channel(channel_id)

                        embed = discord.Embed(
                            title="Ticket Status Update",
                            description="The current ticket status is now ` INACTIVE ` as the user has not responded within 2 hours."
                        )
                        await channel.send(embed=embed)

                        self.bot.inactive_ticket.append(user_id)
                    # Otherwise, it hasn't been 2 hours, so return
                    else:
                        return

    """
    Only run once on cog load, will alert any users that had an open ticket
    of the bots downtime and then resets the database
    """
    @tasks.loop(count=1)
    async def check_for_ticket_reopen(self):
        await self.bot.wait_until_ready()

        temp = self.bot.tempdb.execute("SELECT * FROM temp")
        temp = temp.fetchall()
        supporttemp = self.bot.tempdb.execute("SELECT * FROM supporttemp")
        supporttemp = supporttemp.fetchall()
        data = temp + supporttemp

        embed = discord.Embed(
            title="Bot Downtime - Please Reopen Ticket",
            description="The FrontLines but unfortunately faced some down time. Due to this unexpected downtime, all users whose tickets were in queue or in progress with a volunteer have been ended. Please reopen a ticket with the bot. Sorry for the inconvenience.",
            color=0x0079FF
        )

        server = await self.bot.fetch_guild(MAIN_SERVER)

        for entry in data:
            user_id = entry[0]
            channel_id = entry[1]
            user = self.bot.get_user(user_id)
            try:
                channel = await server.fetch_channel(channel_id)
                await channel.delete()
            except:
                pass

            try:
                await user.send(embed=embed)
            except:
                pass

        self.bot.tempdb.execute("DELETE FROM temp")
        self.bot.tempdb.execute("DELETE FROM supporttemp")
        self.bot.tempdb.commit()


async def setup(bot):
	await bot.add_cog(updates(bot))