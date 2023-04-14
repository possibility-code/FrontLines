import discord
from reader import MAIN_SERVER
from views.support_view import support_view
import datetime


async def claim_support(bot, interaction):
    if interaction.user.id not in bot.online_volunteers:
        embed = discord.Embed(
            title="You Are Not Clocked In!",
            description="The database shows that you are not currently clocked in. You must be clocked in to connect with users. Please note, if you just clocked in please allow up to 1 minute for the data to sync with the bot.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    # Grab the the first user from the support queue
    try:
        user_id = bot.support_queue[0]
    except IndexError:
        embed = discord.Embed(
            title="No Tickets In Queue",
            description="There are no tickets in the queue to claim.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    user = bot.get_user(user_id)

    # Remove the user_id from the support queue
    bot.support_queue.remove(user_id)

    main_server = bot.get_guild(MAIN_SERVER)

    # Create the channel and set the permissions
    channel = await main_server.create_text_channel(f"support-{user.name}")
    try:
        await channel.set_permissions(main_server.default_role, read_messages=False)
        await channel.set_permissions(user, read_messages=True, send_messages=True)
    except:
        with open("error.log", "a") as f:
            f.write(f"{datetime.datetime.now()}: SupportChannelPermissionError\n")
        pass

    bot.support_channel_to_user[channel.id] = user_id

    # Update the support_info dict
    bot.support_info[user_id]["vol_id"] = interaction.user.id
    bot.support_info[user_id]["channel_id"] = channel.id

    # Update supporttemp table
    bot.tempdb.execute("UPDATE supporttemp SET channel_id = ? WHERE user_id = ?", (channel.id, user_id))
    bot.tempdb.commit()

    # Make sure all manager roles have access to the channel
    async with bot.db.acquire() as conn:
        roles = await conn.fetch("SELECT role_id FROM manager_roles WHERE guild_id = $1", MAIN_SERVER)

    # For each role, attempt to set the correct permissions. If it fails the role was
    # likely deleted, so just pass
    for role in roles:
        try:
            await channel.set_permissions(main_server.get_role(role[0]), read_messages=True, send_messages=True)
        except:
            pass

    # Insert new row into the support_count table
    async with bot.db.acquire() as conn:
        await conn.execute("INSERT INTO support_count (date) VALUES ($1)", datetime.date.today())

    # Update temp data into the supporttemp table
    bot.tempdb.execute("UPDATE supporttemp SET channel_id = ? WHERE user_id = ?", (channel.id, user_id))
    bot.tempdb.commit()

    guild = bot.get_guild(bot.support_info[user_id]["guild_id"])
    inv_channel = guild.text_channels[0]
    invite = await inv_channel.create_invite(max_age=0, max_uses=0, reason="Support Ticket", unique=True)

    embed = discord.Embed(
        title="Bot Support Ticket",
        description="Please join the server with the invite below and help to server owners and/or admins with setting up the FrontLines bot in their server.\n\nAsk other admin volunteers for help should you need it on this ticket."
    )
    embed.add_field(name="Server Invite", value=f"[Invite Here]({invite})")
    view = support_view(bot)
    await channel.send(embed=embed, view=view)

    embed = discord.Embed(
        title="Ticket Claimed",
        description="Your ticket has been claimed and the volunteer has been sent an invite to your server. Please be on the lookout for new messages from the volunteer in your server.\n\nBelow you can find the volunteer's information."
    )
    embed.add_field(name="Volunteer", value=f"{user.name}#{user.discriminator}\nID: {user.id}")
    await user.send(embed=embed)

    await interaction.response.send_message(f"Ticket claimed - view {channel.mention}", ephemeral=True)