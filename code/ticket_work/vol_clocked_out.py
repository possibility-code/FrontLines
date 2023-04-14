import discord
import datetime


"""
Put the ticket back into the first position in the queue because the volunteer
that was working on it has clocked out.
"""
async def vol_has_clocked_out(bot, vol_id, user_id):
    # Get the ticket user, volunteer, and the ticket channel
    user = bot.get_user(user_id)
    vol = bot.get_user(vol_id)
    channel_id = bot.ticket_info[user_id]["channel_id"]

    channel = bot.get_channel(channel_id)

    # Edit the current channel permission
    try:
        await channel.set_permissions(vol, read_messages=False, send_messages=False)
    except:
        with open("error.log", "a") as f:
            f.write(f"{datetime.datetime.now()}: ClockoutChannelPermissionError\n")
        pass
    # Insert the user back into the first (zeroth index) of the queue
    bot.ticket_queue.insert(0, user_id)
    del bot.active_ticket[vol_id]

    # Send a message to the user alerting them that their ticket has been sent back to the first position in the queue
    embed = discord.Embed(
        title="Volunteer Clocked Out",
        description="The volunteer that was in charge of your ticket has clocked out for now. Your ticket has been return back to the first position in the queue and will be claimed shortly."
    )
    await user.send(embed=embed)
    # Send a message to the channel stating that the volunteer has clocked out and the ticket has been requeued
    embed = discord.Embed(
        title="Volunteer Clocked Out",
        description="The volunteer that was in charge of this ticket has clocked out. The ticket has been returned to the first position in the queue."
    )
    await channel.send(embed=embed)