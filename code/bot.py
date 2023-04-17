import discord
from discord.ext import commands
import os
from reader import TOKEN, DEFAULT_PREFIX, FRONTLINES_URI_CONNECTION_STRING, MAIN_SERVER
import asyncpg
import sqlite3

async def initialise():
    bot.db = await asyncpg.create_pool(FRONTLINES_URI_CONNECTION_STRING)
    await bot.db.execute("CREATE TABLE IF NOT EXISTS ticket_info (time_started DATE, time_ended DATE, wait_time TEXT, user_id BIGINT, vol_id BIGINT, ticket_messages TEXT, ticket_num SERIAL NOT NULL, category TEXT, reason_of_closure TEXT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS wait_time (date DATE, hour INT, wait_time TEXT, PRIMARY KEY (date, hour))")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS server_info (guild_id BIGINT, message_id BIGINT, channel_id BIGINT, everyone_role BIGINT, PRIMARY KEY (guild_id))")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS consent (user_id BIGINT, waiver TEXT, save_consent TEXT, PRIMARY KEY (user_id))")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS ticket_count (date DATE, count SERIAL NOT NULL)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS main_messages (guild_id BIGINT, dashboard_message_id BIGINT, support_message_id BIGINT, category_message_id BIGINT, statistics_message_id BIGINT, settings_message_id BIGINT, PRIMARY KEY (guild_id))")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS manager_roles (guild_id BIGINT, role_id BIGINT, PRIMARY KEY (guild_id, role_id))")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS support_count (date DATE, count SERIAL NOT NULL)")

    bot.tempdb = sqlite3.connect('temp.sqlite')
    bot.tempdb.execute("CREATE TABLE IF NOT EXISTS temp (user_id BIGINT, channel_id BIGINT, PRIMARY KEY (user_id))")
    bot.tempdb.execute("CREATE TABLE IF NOT EXISTS supporttemp (user_id BIGINT, channel_id BIGINT, PRIMARY KEY (user_id))")
    bot.tempdb.commit()

    bot.remdb = sqlite3.connect('remdb.sqlite')
    bot.remdb.execute("CREATE TABLE IF NOT EXISTS reminders (user_id, recurring, recur_time, message, PRIMARY KEY (user_id, recur_time, message))")
    bot.remdb.execute("CREATE TABLE IF NOT EXISTS timezone (user_id, timezone, PRIMARY KEY (user_id))")
    bot.remdb.commit()

    bot.thanksdb = sqlite3.connect('thanksdb.sqlite')
    bot.thanksdb.execute("CREATE TABLE IF NOT EXISTS thankyou (user_id, thanked_user_id, reason, timestamp)")
    bot.thanksdb.commit()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix=DEFAULT_PREFIX,
        intents = intents
    )

    async def setup_hook(self):
        await initialise()
        for ext in os.listdir('./code/cogs'):
            if ext.endswith('.py'):
                await self.load_extension(f'cogs.{ext[:-3]}')

bot = MyBot()


bot.queue_times = {} # user_id: time
bot.ticket_queue = [] # user_id
bot.still_answering = [] # user_id
bot.avg_wait = "UNKNOWN"
bot.answers = {} # user_id:answers
bot.active_ticket = {} #vol_id:user_id
bot.channel_to_user = {} #channel_id:user_id
bot.ticket_info = {}
bot.inactive_ticket = [] # user_id
"""
user_id: {
    "time_opened": time,
    "time_started": time,
    "time_ended": time,
    "vol_id": vol_id,
    "ticket_messages": [{
        "message": message,
        "time": time,
        "author_name": author_name,
        "author_pfp": author_pfp
    }]
    "ticket_num": ticket_num,
    "category": category,
    "reason_of_closure": reason_of_closure,
    "user_last_responded": time,
    "last_message": message object,
    "channel_id": channel_id
}
"""
bot.queue_status = "enabled"
bot.online_volunteers = []

bot.support_queue = [] # owner_id
bot.support_channel_to_user = {} # channel_id: owner_id
bot.support_active = [] # owner_id
bot.support_info = {}
"""
user_id: {
    "guild_id": guild_id,
    "vol_id": vol_id,
    "channel_id": channel_id,
}
"""

bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

if __name__ == '__main__':
    bot.run(TOKEN)
