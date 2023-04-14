import discord
import asyncio
from reader import MAIN_SERVER
import datetime


"""
Transfers the ticket to a new volunteer. Mainly just changes to channel permissions
so that only the new volunteer can view it.
"""
async def transfer_ticket(bot, interaction, new_vol):
    # Get the ticket user, main server, original volunteer, and the ticket channel
    user = bot.get_user(bot.active_ticket[interaction.user.id])
    main_server = bot.get_guild(MAIN_SERVER)
    orig_vol = main_server.get_member(interaction.user.id)

    for key, value in bot.channel_to_user.items():
        if value == user.id:
            channel_id = key
            break

    channel = main_server.get_channel(channel_id)

    # Edit the confirmation message to show that the ticket transfer will occur in 5 seconds
    embed = discord.Embed(
        title="Ticket Transfer",
        description=f"This ticket will be transferred to {new_vol.name} in 5 seconds.",
        color=discord.Color.green()
    )
    await interaction.response.edit_message(embed=embed, view=None)

    await asyncio.sleep(5)

    del bot.active_ticket[interaction.user.id]
    bot.active_ticket[new_vol.id] = user.id

    # Change channel perms so only the new volunteer can view the channel
    try:
        await channel.set_permissions(new_vol, read_messages=True, send_messages=True)
        await channel.set_permissions(orig_vol, read_messages=False, send_messages=False)
    except:
        with open("error.log", "a") as f:
            f.write(f"{datetime.datetime.now()}: TransferChannelPermissionError\n")
        pass

    # Send a message to the user alerting them that their ticket has been transfered to a new volunteer
    embed = discord.Embed(
        title="Ticket Transfer",
        description=f"Your ticket has been transferred to `{new_vol.name}#{new_vol.discriminator}` in the Possibility server. Your message history will be reviewed by the volunteer, and you will recieve a message from them shortly."
    )
    await user.send(embed=embed)