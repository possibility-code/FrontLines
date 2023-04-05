import discord
from discord.ext import commands
from reader import NEW_SERVERS_CHANNEL
import datetime

"""
Whenever the bot joins a guild we attempt to send the owner a message explaining how to setup the bot, we also
send a message to the NEW_SERVERS_CHANNEL channel in the support server letting the staff know that the bot
has been added to a new server.
"""
class on_guild_join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = discord.Embed(
            title="Time for setup!",
            description="Below is a list of instructions for proper setup. Please follow this list in order to allow me to get working in your server!",
            color=0xC1FFD7,
        )
        embed.add_field(name="Step 1: Hoist Me", value=f"Make sure you move my role, `{self.bot.user.name}`, above the role that your members have. This allows me to be able to properly interact with users and open tickets.")
        embed.add_field(name="Step 2: /setup", value="Now please run the `/setup` command in your server. This command will need you to provide some information, such as category and channel names. After you run this command, I will create a new category and channel that will allow your members to open tickets.")
        embed.set_footer(text="Thank you for using me!")

        guild_owner = guild.owner
        try:
            await guild_owner.send(embed=embed)
        except:
            pass


        channel = self.bot.get_channel(NEW_SERVERS_CHANNEL)
        embed = discord.Embed(
            title="FrontLines has been added to a new server!",
        )
        embed.add_field(name="Server Name", value=f"```{guild.name}```", inline=True)
        embed.add_field(name="Server ID", value=f"```{guild.id}```", inline=True)
        embed.add_field(name="# of Members", value=f"```{guild.member_count}```", inline=True)
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass
        embed.set_footer(text=f"Server joined at {datetime.datetime.now()} UTC")

        await channel.send(embed=embed)


async def setup(bot):
	await bot.add_cog(on_guild_join(bot))