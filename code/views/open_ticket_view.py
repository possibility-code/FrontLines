import discord
import asyncpg
import datetime
import asyncio
from reader import DASHBOARD_CHANNEL

"""
When a ticket is opened, the user must answer some questions first

Firstly we ask their mood and give them 5 buttons to select from
"""
class open_ticket_question_one(discord.ui.View):
    def __init__(self, bot, interaction, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.interaction = interaction

    @discord.ui.button(emoji="😃", style=discord.ButtonStyle.grey, row=1)
    async def smiley(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** Whats your age?",
        )
        file = discord.File("./code/img/age.png", filename="age.png")
        embed.set_image(url="attachment://age.png")
        view = open_ticket_question_two(self.bot, interaction, self.guild_id, "😃")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(emoji="🙂", style=discord.ButtonStyle.grey, row=1)
    async def slight_smile(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** Whats your age?",
        )
        file = discord.File("./code/img/age.png", filename="age.png")
        embed.set_image(url="attachment://age.png")
        view = open_ticket_question_two(self.bot, interaction, self.guild_id, "🙂")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(emoji="😐", style=discord.ButtonStyle.grey, row=1)
    async def neutral_face(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** Whats your age?",
        )
        file = discord.File("./code/img/age.png", filename="age.png")
        embed.set_image(url="attachment://age.png")
        view = open_ticket_question_two(self.bot, interaction, self.guild_id, "😐")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(emoji="☹️", style=discord.ButtonStyle.grey, row=1)
    async def frowning(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** Whats your age?",
        )
        file = discord.File("./code/img/age.png", filename="age.png")
        embed.set_image(url="attachment://age.png")
        view = open_ticket_question_two(self.bot, interaction, self.guild_id, "☹️")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(emoji="😭", style=discord.ButtonStyle.grey, row=1)
    async def sob(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** Whats your age?",
        )
        file = discord.File("./code/img/age.png", filename="age.png")
        embed.set_image(url="attachment://age.png")
        view = open_ticket_question_two(self.bot, interaction, self.guild_id, "😭")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)


"""
Second question requires the user to select their age range
Prefer Not To Answer is also an option

When they answer, send them to the next question (reason_view)
"""

class open_ticket_question_two(discord.ui.View):
    def __init__(self, bot, interaction, guild_id, mood):
        super().__init__()
        self.bot = bot
        self.mood = mood
        self.guild_id = guild_id
        self.interaction = interaction

    @discord.ui.button(label="13-15", style=discord.ButtonStyle.grey, row=1)
    async def to_15(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "13-15")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(label="16-17", style=discord.ButtonStyle.grey, row=1)
    async def to_17(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "16-17")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(label="18-21", style=discord.ButtonStyle.grey, row=1)
    async def to_21(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "18-21")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(label="22-27", style=discord.ButtonStyle.grey, row=1)
    async def to_27(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "22-27")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(label="28+", style=discord.ButtonStyle.grey, row=1)
    async def over_28(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "18+")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)

    @discord.ui.button(label="Prefer not to answer", style=discord.ButtonStyle.grey, row=2)
    async def reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description = f"**Question |** What's the reason for opening a ticket?\n\nPlease select one of the options from the dropdown below",
        )
        file = discord.File("./code/img/forums.png", filename="forums.png")
        embed.set_image(url="attachment://forums.png")
        view = reason_view(self.bot, interaction, self.guild_id, self.mood, "Prefer not to answer")
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view)


"""
View created in order to attach the dropdown
"""
class reason_view(discord.ui.View):
    def __init__(self, bot, interaction, guild_id, mood, age):
        super().__init__()
        self.add_item(reason_dropdown(bot, interaction, guild_id, mood, age))

class reason_dropdown(discord.ui.Select):
    def __init__(self, bot, interaction, guild_id, mood, age):
        options = [
            discord.SelectOption(label='Anxiety'),
            discord.SelectOption(label='Bereavement'),
            discord.SelectOption(label='Bullying'),
            discord.SelectOption(label='Depression'),
            discord.SelectOption(label='Eating Disorders'),
            discord.SelectOption(label='Family Issues'),
            discord.SelectOption(label='Friend Issues'),
            discord.SelectOption(label='Health Concerns'),
            discord.SelectOption(label='Isolation'),
            discord.SelectOption(label='LGBTQ+ Issues'),
            discord.SelectOption(label='Physical Abuse'),
            discord.SelectOption(label='Relationship Issues'),
            discord.SelectOption(label='School Problems'),
            discord.SelectOption(label='Self-Harm'),
            discord.SelectOption(label='Sexual Abuse'),
            discord.SelectOption(label='Stress'),
            discord.SelectOption(label='Substance Abuse'),
            discord.SelectOption(label='Suicidal Thoughts'),
            discord.SelectOption(label='Other')
        ]

        super().__init__(placeholder='Choose a reason...', min_values=1, max_values=1, options=options)
        self.bot = bot
        self.interaction = interaction
        self.guild_id = guild_id
        self.mood = mood
        self.age = age

    """
    When a response is chosen, we update the ticket_count table and add the user to the queue
    """
    async def callback(self, interaction: discord.Interaction):
        await self.bot.db.execute("INSERT INTO ticket_count (date) VALUES ($1)", datetime.date.today())

        queue_position = len(self.bot.ticket_queue) + 1

        self.bot.ticket_info[interaction.user.id] = {
            "time_opened": datetime.datetime.now(),
            "time_started": None,
            "time_ended": None,
            "vol_id": None,
            "ticket_messages": [],
            "ticket_num": None,
            "category": self.values[0],
            "reason_of_closure": None,
            "user_last_responded": None,
            "last_message": None,
            "channel_id": None
        }

        # Send the user a message to let them know they have been added to the queue
        # NOTE: This doesn't currently update information like the average wait time or
        # current queue position, but it can easily be setup to do this every x amount of time
        embed = discord.Embed(
            title="Ticket Opened!",
            description=f"Your ticket has been opened, and you have been entered into the queue",
            color=0x0079FF
        )
        embed.add_field(name="Queue Position", value=f"` {queue_position} `", inline=False)
        embed.add_field(name=f"Average Wait Time [ Right Now ]", value=f"` {self.bot.avg_wait} `", inline=False)
        embed.add_field(name="Active Support Volunteers", value=f"` {len(self.bot.online_volunteers)} `", inline=False)
        embed.add_field(name="**Notice**", value="We are not a crisis service, and in the event of a crisis, our job is to help guide members toward local crisis support.\n\n__Are you in a crisis__?\nCall 800-273-8255 or text POSSIBILITY to 741741")

        await interaction.response.edit_message(attachments=[], embed=embed, view=None)

        self.bot.ticket_queue.append(interaction.user.id)
        # Add the users answers to the 'answers' dictionary
        # Answers are sent between '+' so that they can easily be split
        # later when the ticket is claimed
        self.bot.answers[interaction.user.id] = f"{self.mood}+{self.age}+{self.values[0]}"

        self.bot.still_answering.remove(interaction.user.id)

        # Ping everyone in the dashboard channel so that they know a ticket has been opened
        dash_channel = self.bot.get_channel(DASHBOARD_CHANNEL)
        msg = await dash_channel.send("@everyone")
        await asyncio.sleep(0.5)
        await msg.delete()

        # Add the users id to the temp.sqlite database (if the bot goes down while the ticket
        # is in the queue or in progress, we will message these users when the bot comes back
        # online to tell them to reopen a new ticket)
        self.bot.tempdb.execute("INSERT INTO temp VALUES (?, ?)", (interaction.user.id, 0))
        self.bot.tempdb.commit()