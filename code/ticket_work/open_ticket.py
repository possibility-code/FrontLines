import discord
from views.open_ticket_view import open_ticket_question_one
from views.waiver_view import sign_waiver_view

"""
Determine whether or not the user is currently eligble to open a ticket,
if they are, send them to the questions that must be answered before ticket opening.
"""
async def open_ticket(bot, interaction):
    if interaction.user.id in bot.ticket_queue or bot.ticket_queue or bot.still_answering:
        embed = discord.Embed(
            title="Ticket Already Open",
            description="You already have a ticket open. Please close it before opening a new one."
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if bot.queue_status == "disabled":
        embed = discord.Embed(
            title="Queue Disabled",
            description="The queue is currently disabled. This action was done by one of the managers in the Possibility server in order to temporarily stop users from opening new tickets. Please try again later.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Grab the users waiver information
    async with bot.db.acquire() as conn:
        waiver = await conn.fetchval("SELECT waiver, save_consent FROM consent WHERE user_id = $1", interaction.user.id)
        # If the user hasn't signed the waiver, send them to the waiver view in their DMs
        if not waiver:
            embed = discord.Embed(
                title = "WAIVER",
                description = f"we are not a 24/7 service. Instead, our operation hours are determined by staffing and availability. If volunteers are working, we are working; this does not mean we will be able to get to you instantly. Although we will always try to keep our times low, it's not our primary goal. Instead, our goal is to provide a meaningful impact on your life.\n\nWe are not a crisis service, and in the event of a crisis, out job is to help guide our members to local crisis support.\n\nYour support sessions can be terminated for making volunteers feel uncomfortable, or for breaking Discord ToS. We also will keep a transcript of the messages sent in the ticket.\n\nAt the bottom of this message is a button named `Sign Waiver`. Clicking this button acknowledges that you have read this waiver and gives us the ability to help you find resources or a place for you to express yourself. After clicking this button, this message will be edited and you will be required to answer 1 question before you can open a ticket.",
                color = 0x0079FF
            )
            view = sign_waiver_view(bot)
            # Try to send them the message and defer the interation
            try:
                await interaction.user.send(embed=embed, view=view)
                return await interaction.response.defer()
            # Except if they have their DMs closed
            except discord.Forbidden:
                embed = discord.Embed(
                    title = "DMs Not Open!",
                    description = "Your DMs are closed. Please open them and try again.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)


    # If the user can open a ticket, we send their first question
    try:
        await interaction.response.defer()
        bot.still_answering.append(interaction.user.id)

        embed = discord.Embed(
            title = "You must answer 3 questions before you can open a ticket.",
            description="**Question |** What best describes your current mood?"
        )
        file = discord.File("./code/img/mood_table.png", filename="mood_table.png")
        embed.set_image(url="attachment://mood_table.png")
        view = open_ticket_question_one(bot, interaction, interaction.guild.id)

        await interaction.user.send(file=file, embed=embed, view=view)

    # Except if they have their DMs closed
    except discord.errors.Forbidden:
        embed = discord.Embed(
            title="DMs Not Open!",
            description="In order to keep your privacy, tickets are handled through direct messages with the bot. In order to open a ticket, you must have your DMs open so that the bot can message you. Try again after opening your DMs.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)