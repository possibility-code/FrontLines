import discord
import asyncio

"""
Puts the ticket back into the queue in the first position so
that another volunteer can quickly pick it up.
"""
async def requeue_ticket(bot, interaction):
    user = bot.get_user(bot.active_ticket[interaction.user.id])
    vol = bot.get_user(interaction.user.id)

    # Edit the confirmation message to show that the ticket transfer will occur in 5 seconds
    # This is more for posterity and doesn't really do anything. A cancel button could be added
    # but now the view is set to None
    embed = discord.Embed(
        title="Ticket Requeue",
        description="This ticket will be sent back to the queue in 5 seconds.",
        color=discord.Color.green()
    )
    await interaction.response.edit_message(embed=embed, view=None)
    msg = await interaction.original_response()

    # Sleep for 5 seconds
    await asyncio.sleep(5)
    await msg.delete()

    # Try to delete the user from the 'active_ticket' dict if they are in there
    for key, value in bot.active_ticket.items():
        if value == user.id:
            del bot.active_ticket[key]
            break

    for key, value in bot.channel_to_user.items():
        if value == user.id:
            channel_id = key
            break

    channel = bot.get_channel(channel_id)

    # Edit the current channel permission
    await channel.set_permissions(vol, read_messages=False, send_messages=False)
    # Insert the user back into the first (zeroth index) of the queue
    bot.ticket_queue.insert(0, user.id)

    # Send a message to the user alerting them that their ticket has been sent back to the first position in the queue
    embed = discord.Embed(
        title="Ticket Requeue",
        description="Your ticket has been sent back to the first position in the queue. You will be notified when it is assigned to a volunteer."
    )
    await user.send(embed=embed)
    # Send a message to the channel stating that the ticket has been requeued
    embed = discord.Embed(
        title="Ticket Requeue",
        description="This ticket has been requeued and sent back to the first position in the queue."
    )
    await channel.send(embed=embed)