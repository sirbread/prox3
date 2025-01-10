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
        self.last_poll_timestamps = {} 
        self.poll_votes = {}

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
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            await interaction.response.send_message(
                f"You can send another confession in {minutes} minutes and {seconds} seconds.", 
                ephemeral=True
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
        last_poll_time = bot.last_poll_timestamps.get(user_id, 0)
        time_diff = current_time - last_poll_time

        if time_diff < 1800:  
            remaining_time = int(1800 - time_diff)
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            await interaction.response.send_message(
                f"You can create another poll in {minutes} minutes and {seconds} seconds.", 
                ephemeral=True
            )
            return

        options = [op for op in [op1, op2, op3, op4] if op]
        if len(options) < 2 or len(options) > 4:
            await interaction.response.send_message("Please provide between 2 and 4 options for the poll.", ephemeral=True)
            return

        bot.last_poll_timestamps[user_id] = current_time

        embed = discord.Embed(
            title=message,
            description="\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]),
            color=discord.Color.blurple()
        )

        poll_message = await interaction.channel.send(embed=embed, view=PollView(options))
        await interaction.response.send_message("Anonymous poll has been created!", ephemeral=True)

class PollView(discord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.poll_votes = [0] * len(options)
        self.voters = set()
        self.message = None

    @discord.ui.button(label="1️⃣", style=discord.ButtonStyle.primary)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, 0)

    @discord.ui.button(label="2️⃣", style=discord.ButtonStyle.primary)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, 1)

    @discord.ui.button(label="3️⃣", style=discord.ButtonStyle.primary)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, 2)

    @discord.ui.button(label="4️⃣", style=discord.ButtonStyle.primary)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, 3)

    async def handle_vote(self, interaction: discord.Interaction, option_index: int):
        if option_index >= len(self.options):
            await interaction.response.send_message("This option is not available.", ephemeral=True)
            return

        user_id = interaction.user.id
        if user_id in self.voters:
            await interaction.response.send_message("You've already voted!", ephemeral=True)
            return

        self.voters.add(user_id)
        self.poll_votes[option_index] += 1

        new_embed = discord.Embed(
            title=interaction.message.embeds[0].title,
            description="\n".join([f"{i+1}. {opt} - {votes} votes" for i, (opt, votes) in enumerate(zip(self.options, self.poll_votes))]),
            color=discord.Color.blurple()
        )

        await interaction.message.edit(embed=new_embed, view=self)
        await interaction.response.send_message("Your vote has been recorded!", ephemeral=True)

load_dotenv()
token = os.getenv("BOT_TOKEN")
bot.run(token)
