import discord
from reader import MAIN_SERVER
import datetime
from views.new_ticket_view import new_ticket_view


async def claim_ticket(bot, interaction):
    if interaction.user.id not in bot.online_volunteers:
        embed = discord.Embed(
            title="You Are Not Clocked In!",
            description="The database shows that you are not currently clocked in. You must be clocked in to connect with users. Please note, if you just clocked in please allow up to 1 minute for the data to sync with the bot.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    try:
        user_id = bot.ticket_queue[0]
    except IndexError:
        embed = discord.Embed(
            title="No Tickets In Queue",
            description="There are no tickets in the queue to claim.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    user = bot.get_user(user_id)

    bot.ticket_queue.remove(user_id)
    # Add the user to the 'active_ticket' dictionary and get the main server
    bot.active_ticket[interaction.user.id] = user_id
    main_server = bot.get_guild(MAIN_SERVER)

    # If there is not time_started, that means its the first time the ticket is being claimed
    # so calc the wait time, do NOT do this if the ticket is being re-claimed
    if not bot.ticket_info[user_id]["time_started"]:
        start_date = bot.ticket_info[user_id]["time_opened"]
        start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S.%f")

        end_date = datetime.datetime.now()
        end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S.%f")

        wait_time = end_date - start_date

    else:
        wait_time = bot.ticket_info[user_id]["time_started"] - bot.ticket_info[user_id]["time_opened"]

    # Formate wait_time to just HH:MM:SS
    wait_time = str(wait_time).split(".")[0]

    bot.ticket_info[user_id]["time_started"] = datetime.datetime.strptime(str(datetime.datetime.now()), "%Y-%m-%d %H:%M:%S.%f")

    if bot.avg_wait == "UNKNOWN":
        bot.avg_wait = wait_time
    else:
        # bot.avg_wait is a string in the format of HH:MM:SS
        # so we need to convert it to seconds to do math
        avg_wait = bot.avg_wait.split(":")
        avg_wait = int(avg_wait[0]) * 3600 + int(avg_wait[1]) * 60 + int(avg_wait[2])

        wait_time = wait_time.split(":")
        wait_time = int(wait_time[0]) * 3600 + int(wait_time[1]) * 60 + int(wait_time[2])
        # Calculate the new average wait time
        bot.avg_wait = (avg_wait + wait_time) / 2
        # Convert the new average wait time to HH:MM:SS
        bot.avg_wait = str(datetime.timedelta(seconds=bot.avg_wait)).split(".")[0]

    # If the channel is already created, that means it was requeued for some
    # reason, so just get the channel and change the permissions
    if bot.ticket_info[user_id]["channel_id"]:
        channel = bot.get_channel(bot.ticket_info[user_id]["channel_id"])

        # Change channel perms so only the volunteer can view the channel
        try:
            await channel.set_permissions(main_server.get_member(interaction.user.id), read_messages=True, send_messages=True)
            await channel.set_permissions(main_server.default_role, read_messages=False, send_messages=False)
        except:
            with open("error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: TicketChannelPermissionError\n")
            pass

        # Send a message to the user notifying them that their ticket has been claimed
        embed = discord.Embed(
            title="Your Ticket Has Been Re-claimed",
            description="This ticket has been re-claimed by a volunteer. Please allow time for the volunteer to read over previous messages, thank you."
        )
        await user.send(embed=embed)

        # Send a message to the channel notifying the volunteer to read previous messages
        embed = discord.Embed(
            title="Read Previous Messages",
            description="This ticket has been previously claimed by a volunteer. Please go to the top of this channel and read through the previous messages in order to help this user."
        )
        await channel.send(embed=embed)
    # Else, create a new channel
    else:
        channel = await main_server.create_text_channel(name=f"bothelp-{user.name}")

        # Add the channel id to the temp database
        bot.tempdb.execute(f"UPDATE temp SET channel_id = {channel.id} WHERE user_id = {user_id}")
        bot.tempdb.commit()

        # Change channel perms so only the volunteer can view the channel
        try:
            await channel.set_permissions(main_server.get_member(interaction.user.id), read_messages=True, send_messages=True)
            await channel.set_permissions(main_server.default_role, read_messages=False, send_messages=False)
        except:
            with open("error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: TicketChannelPermissionError\n")
            pass

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

        async with bot.db.acquire() as conn:
            ticket = await conn.fetch("SELECT count FROM ticket_count")

        ticket_num = 0

        for entry in ticket:
            ticket_num += 1

        # Create the auto-send embed, and give it the 'new_ticket_view', then send it to the channel
        # Get all of the users answers by splitting at '+' then add them to the embed
        answers = bot.answers[user_id].split("+")

        del bot.answers[user_id]

        embed = discord.Embed(
            title="Possbility ♾️ Frontlines",
            description=f"`{user.name}#{user.discriminator}` | `{user_id}`"
        )

        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="STATUS", value="```Active```", inline=True)
        embed.add_field(name="CODE", value="```None```", inline=True)
        embed.add_field(name="SUPPORTER", value=f"```{interaction.user.name}```", inline=True)
        embed.add_field(name="ANSWERS", value=f"Mood: ```{answers[0]}```Age: ```{answers[1]}```Reason: ```{answers[2]}```", inline=False)
        embed.set_footer(text=f"Ticket {ticket_num} | Claimed on {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        view = new_ticket_view(bot)
        await channel.send(embed=embed, view=view)

        # Create the 'Standard Automatic Message' and send it to the user and the channel
        embed = discord.Embed(
            title="Standard Automatic Message",
            description=f"Hey {user.name}, I'm a member of the Possibility volunteer team. I've read the answers to the questions the bot asked you.\n\nHow are you feeling?"
        )
        embed.set_footer(text=f"Ticket {ticket_num} | Claimed on {datetime.date.today()} at {datetime.datetime.now().strftime('%H:%M:%S')}")

        await channel.send(embed=embed)
        await user.send(embed=embed)

        # Update bot.ticket_info
        bot.ticket_info[user_id]["time_started"] = datetime.datetime.now()
        bot.ticket_info[user_id]["vol_id"] = interaction.user.id
        bot.ticket_info[user_id]["ticket_num"] = ticket_num
        bot.ticket_info[user_id]["category"] = answers[2]
        bot.ticket_info[user_id]["channel_id"] = channel.id

        bot.channel_to_user[channel.id] = user_id

    # Defer the interaction
    await interaction.response.defer()