from discord.ext import commands
from discord import app_commands
import discord
import re
import os
from dotenv import load_dotenv
import time

class AnonymousMessageBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.last_confession_timestamps = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("synced cmds")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("bot ready")

bot = AnonymousMessageBot()

def extract_confession_number(content):
    match = re.search(r"Confession #(\d+)", content)
    if match:
        return int(match.group(1))
    return 0

@bot.tree.command(name="prox3", description="Send an anonymous message or confession.")
@app_commands.describe(
    message_type="Choose between 'confession', 'message', or 'poll'",
    message="The content of your anonymous message or confession"
)
@app_commands.choices(
    message_type=[
        app_commands.Choice(name="Confession", value="confession"),
        app_commands.Choice(name="Message", value="message"),
        app_commands.Choice(name="Poll", value="poll"),
    ]
)

async def prox3(interaction: discord.Interaction, message_type: app_commands.Choice[str], message: str, op1: str = None, op2: str = None, op3: str = None, op4: str = None):
    user_id = interaction.user.id
    current_time = time.time()

    if message_type.value == "confession":
        last_time = bot.last_confession_timestamps.get(user_id, 0)
        time_diff = current_time - last_time

        if time_diff < 600:  
            remaining_time = int(600 - time_diff)
            await interaction.response.send_message(
                f"You can send another confession in {remaining_time} seconds.", ephemeral=True
            )
            return

        bot.last_confession_timestamps[user_id] = current_time
        await interaction.response.send_message("Your anonymous confession has been sent!", ephemeral=True)

        confession_number = 1
        async for msg in interaction.channel.history(limit=100): 
            if msg.author == bot.user and msg.embeds:
                embed = msg.embeds[0]
                if embed.title and embed.title.startswith("Confession #"):
                    confession_number = extract_confession_number(embed.title)
                    if confession_number > 0:
                        confession_number += 1
                        break

        embed = discord.Embed(
            title=f"Confession #{confession_number}",
            description=message,
            color=discord.Color.blurple()
        )
        await interaction.channel.send(embed=embed)

    elif message_type.value == "message":
        await interaction.response.send_message("Your anonymous message has been sent!", ephemeral=True)
        await interaction.channel.send(message)

    elif message_type.value == "poll":
        options = [op for op in [op1, op2, op3, op4] if op]
        if len(options) < 2 or len(options) > 4:
            await interaction.response.send_message("Please provide between 2 and 4 options for the poll.", ephemeral=True)
            return

        poll_embed = discord.Embed(
            title=message,
            description="\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]),
            color=discord.Color.blurple()
        )

        poll_msg = await interaction.channel.send(embed=poll_embed)
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        for i in range(len(options)):
            await poll_msg.add_reaction(reactions[i])

        await interaction.response.send_message("Anonymous poll has been created!", ephemeral=True)

load_dotenv()
token = os.getenv("BOT_TOKEN")
bot.run(token)
