import discord
import asyncio
import datetime
import json
from jinja2 import Environment, FileSystemLoader
import json
from pathlib import Path

"""
Confirmation for closing a ticket
"""
class confirm_close(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.red, row=1)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await close_ticket(self.bot, interaction, self.user_id)

"""
Goes through the procedures that must be done prior to actually closing the ticket,
then we run 'close_ticket' when the confirmation button is pressed
"""
async def button_close_ticket(bot, interaction):
    user_id = bot.channel_to_user[interaction.channel.id]

    # Send the message in the channel telling the volunteer to provide a reason for closing
    # the ticket within brackets (e.g. [reason])
    embed = discord.Embed(
        title="Reason for Closure",
        description="In order to close this ticket, you must provide a reason for closure. Please send a message within the next 3 minutes in order to close the ticket\n\n**NOTE: Your message MUST be sent within `[` and `]` in order for it to be read by the bot. Example ` [reason] `**."
    )
    await interaction.response.edit_message(embed=embed, view=None)

    try:
        msg = await bot.wait_for('message', check=lambda message:message.author == interaction.user and message.channel.id == interaction.channel.id, timeout=180)
    # If there is no response within 3 minutes, send message
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Ticket Closure Time Out",
            description="The ticket closure has timed out as you did not send a reason for closure within the allotted 3 minutes. If you would still like to close the ticket, please try again .",
        )
        # Try to edit the message to show the above embed
        try:
            return await interaction.edit_original_response(embed=embed, view=None)
        # If the message was deleted, we get 'Not Found', so just return
        except discord.errors.NotFound:
            return

    # Check to make sure the message was sent within brackets (e.g. [reason])
    if msg.content.startswith('[') and msg.content.endswith(']'):
        content = msg.content[1:-1]
        bot.ticket_info[user_id]["reason_of_closure"] = content
        # Send the message telling the user to confirm the ticket closure
        embed = discord.Embed(
            title="Confirm Ticket Closing",
            description=f"Press the `Confirm` button below to close the ticket.",
        )
        view = confirm_close(bot, user_id)
        await interaction.edit_original_response(embed=embed, view=view)

    # If the message was not sent within brackets (e.g. [reason]) then send a message
    # to the user alerting them that the ticket will not be closed
    else:
        embed = discord.Embed(
            title="Ticket Closure Cancelled",
            description="You did not provide a reason for closure within `[]`. If you would still like to close the ticket, please try again.",
            color=discord.Color.red()
        )
        return await interaction.edit_original_response(embed=embed, view=None)

# Logic to close the ticket
async def close_ticket(bot, interaction, user_id):
    user = bot.get_user(user_id)

    # Message alerting user ticket will be closing in 5 seconds
    embed = discord.Embed(
        title="Ticket Closing",
        description="Thank you for providing a reason for closure. This ticket will now be closed in 5 seconds.",
        color=discord.Color.green()
    )
    await interaction.response.edit_message(embed=embed, view=None)

    # Sleep for 5 seconds
    await asyncio.sleep(5)

    bot.ticket_info[user_id]["time_ended"] = datetime.datetime.now()

    # Send the user a message alerting them that their ticket has been closed
    embed = discord.Embed(
        title="Ticket Has Been Closed",
        description="Remember, we are here for you, and you can always open a new ticket.",
    )
    file = discord.File("./code/img/space_heart.png", filename="space_heart.png")
    embed.set_thumbnail(url="attachment://space_heart.png")
    await user.send(file=file, embed=embed)

    wait_time = bot.ticket_info[user_id]["time_started"] - bot.ticket_info[user_id]["time_opened"]
    wait_time = str(wait_time).split('.')[0]

    time_started = bot.ticket_info[user_id]["time_started"]
    time_ended = bot.ticket_info[user_id]["time_ended"]
    vol_id = bot.ticket_info[user_id]["vol_id"]
    ticket_num = bot.ticket_info[user_id]["ticket_num"]
    category = bot.ticket_info[user_id]["category"]
    reason_of_closure = bot.ticket_info[user_id]["reason_of_closure"]
    ticket_messages = str(bot.ticket_info[user_id]["ticket_messages"])

    # Insert all of the data into the database
    await bot.db.execute("INSERT INTO ticket_info (time_started, time_ended, wait_time, user_id, vol_id, ticket_messages, ticket_num, category, reason_of_closure) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)", time_started, time_ended, wait_time, user_id, vol_id, ticket_messages, ticket_num, category, reason_of_closure)

    channel = bot.get_channel(bot.ticket_info[user_id]["channel_id"])
    await channel.delete()

    try:
        del bot.active_ticket[vol_id]
    except KeyError:
        pass

    # Delete the user from the temp.sqlite database
    bot.tempdb.execute("DELETE FROM temp WHERE user_id = ?", (user_id,))
    bot.tempdb.commit()

    # Sleep for 3 seconds just to wait for a sec
    await asyncio.sleep(3)

    start_date = time_started.strftime("%d/%m/%Y %H:%M")
    end_date = time_ended.strftime("%d/%m/%Y %H:%M")

    # Get the difference between the start and end date
    difference = time_ended - time_started
    difference = datetime.datetime.strptime(str(difference), "%H:%M:%S.%f")
    difference = difference.strftime("%H:%M:%S")

    messages = []
    # ticket_messages is a list of dicts which are in the format author_id:message


    """
    user_id: {
        "time_opened": time,
        "time_started": time,
        "time_ended": time,
        "vol_id": vol_id,
        "vol_name": vol_name,
        "vol_pfp": vol_pfp,
        "user_name": user_name,
        "user_pfp": user_pfp,
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




    ticket_messages = list(bot.ticket_info[user_id]["ticket_messages"])
    for entry in ticket_messages:
        if entry["author_name"] == user.name:
            color = "color:#7289DA"
        else:
            color = "color:#7ADEAD"
        message = entry["message"]
        time = entry["time"]
        author_name = entry["author_name"]
        author_pfp = entry["author_pfp"]

        my_list = [message, time, author_name, author_pfp, color]
        messages.append(my_list)

    # Get the amount of message sent by getting the lenth of the 'messages' list
    length_num = int(len(messages))
    # If the length is 1 then use the singular (message) else use the plural (messages)
    length = f"{length_num} messages" if length_num != 1 else f"{length_num} message"

    # Define the template and load the Environment using Jinja2 from template.html
    template = Environment(loader=FileSystemLoader('code/templates')).get_template('template.html')

    # Define the path of the new ticket transcript
    path = Path(f"code/templates/transcripts/{ticket_num}.html")
    # Open/create the new file, write all of the template data to it, and then close the file
    file = open(f"code/templates/transcripts/{ticket_num}.html", "w")
    file.write(template.render(ticket_num=ticket_num, user_name=user.name, user_id=user_id, volunteer_id=vol_id, start_date=start_date, end_date=end_date, difference=difference, wait_time=wait_time, length=length, length_num=length_num, messages=messages, reason=reason_of_closure))
    file.close()

    # Attempt to empty ALL dicts and lists no matter what
    try:
        bot.ticket_queue.remove(user_id)
    except ValueError:
        pass
    try:
        bot.still_answering.remove(user_id)
    except ValueError:
        pass
    try:
        del bot.answers[user_id]
    except KeyError:
        pass
    try:
        del bot.channel_to_user[channel.id]
    except KeyError:
        pass
    try:
        for key, value in bot.active_ticket.items():
            if value == user_id:
                del bot.active_ticket[key]
    except RuntimeError:
        pass
    try:
        del bot.ticket_info[user_id]
    except KeyError:
        pass