import discord
from discord.ext import commands
from reader import MAIN_SERVER
from views.gpt_rec_view import gpt_rec_view

"""
On every message, determine if the message needs to be sent a channel (eg, it is part of an active ticket)
If it is, send it to the appropriate channel, otherwise just return
"""
class on_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.bot.channel_to_user.keys():
            if not message.content.startswith('[') and not message.content.endswith(']'):
                # Message from support --> send to user
                try:
                    user = self.bot.get_user(self.bot.active_ticket[message.author.id])
                except KeyError:
                    user = self.bot.get_user(self.bot.channel_to_user[message.channel.id])

                embed = discord.Embed(
                    title=f"Message from Support",
                    description=f"```{message.content}```"
                )
                file = discord.File("./code/img/space_heart.png", filename="space_heart.png")
                embed.set_thumbnail(url="attachment://space_heart.png")
                await user.send(file=file, embed=embed)

                message_info = {
                    "message": message.content,
                    "time": message.created_at.strftime('%Y/%m/%d %H:%M'),
                    "author_name": message.author.name,
                    "author_pfp": message.author.avatar.url
                }

                self.bot.ticket_info[user.id]["ticket_messages"].append(message_info)

        if isinstance(message.channel, discord.DMChannel) and message.author.id in self.bot.active_ticket.values():
            # Message from user --> send to support
            main_server = self.bot.get_guild(MAIN_SERVER)
            channel = main_server.get_channel(self.bot.ticket_info[message.author.id]["channel_id"])

            embed = discord.Embed(
                title=f"Message from {message.author.name}#{message.author.discriminator}",
                description=f"```{message.content}```"
            )
            embed.set_thumbnail(url=message.author.avatar.url)
            view = gpt_rec_view(self.bot.ticket_info[message.author.id]["ticket_messages"])
            msg = await channel.send(embed=embed, view=view)

            message_info = {
                "message": message.content,
                "time": message.created_at.strftime('%Y/%m/%d %H:%M'),
                "author_name": message.author.name,
                "author_pfp": message.author.avatar.url
            }

            self.bot.ticket_info[message.author.id]["ticket_messages"].append(message_info)
            # Update the last message sent (for the gpt recommendation view)
            if self.bot.ticket_info[message.author.id]["last_message"] is not None:
                last_message = self.bot.ticket_info[message.author.id]["last_message"]
                await last_message.edit(view=None)
                self.bot.ticket_info[message.author.id]["last_message"] = msg
            else:
                self.bot.ticket_info[message.author.id]["last_message"] = msg

            # Make sure they are not in the inactive ticket list
            if message.author.id in self.bot.inactive_ticket:
                self.bot.inactive_ticket.remove(message.author.id)


async def setup(bot):
	await bot.add_cog(on_message(bot))