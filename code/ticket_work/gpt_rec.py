import openai
import discord

async def get_gpt_recommendation(messages, interaction):
    last_five_messages = []
    last_five_dicts = messages[-5:]
    for dict in last_five_dicts:
        for key in dict:
            last_five_messages.append(dict[key])

    if len(last_five_messages) < 5:
        for i in range(5 - len(last_five_messages)):
            last_five_messages.append("")

    openai.organization = "org-u28pWacmRKQWYYNAVlaeuMeE"
    openai.api_key = "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"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=75,
        messages=[
                {"role": "system", "content": "You are a volunteer for a mental health hotline and are currently helping a user."},
                {"role": "user", "content": f"{last_five_messages[0]}"},
                {"role": "user", "content": f"{last_five_messages[1]}"},
                {"role": "user", "content": f"{last_five_messages[2]}"},
                {"role": "user", "content": f"{last_five_messages[3]}"},
                {"role": "user", "content": f"{last_five_messages[4]}"}
            ]
    )

    embed = discord.Embed(
        title="Below is a recommendation made by an AI using the most recent messages from this ticket",
        description=f"```{response['choices'][0]['message']['content']}```",
    )

    await interaction.edit_original_response(embed=embed)