import discord
from discord import app_commands
import re
import os
from dotenv import load_dotenv

class AnonymousMessageBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.active_polls = {}  

    async def setup_hook(self):
        await self.tree.sync()
        print("synced cmds")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("bot ready")

bot = AnonymousMessageBot()

def extract_confession_number(content):
    match = re.match(r"Confession #(\d+):", content)
    if match:
        return int(match.group(1))
    return 0

class PollView(discord.ui.View):
    def __init__(self, bot, poll_message_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.poll_message_id = poll_message_id
        self.votes = {"Yes": 0, "No": 0}  

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        if user_id in self.bot.active_polls.get(self.poll_message_id, {}):
            await interaction.response.send_message("You have already voted on this poll!", ephemeral=True)
            return

        self.votes["Yes"] += 1
        self.bot.active_polls.setdefault(self.poll_message_id, {})[user_id] = "Yes"

        await interaction.response.edit_message(content=self.get_poll_results(), view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        if user_id in self.bot.active_polls.get(self.poll_message_id, {}):
            await interaction.response.send_message("You have already voted on this poll!", ephemeral=True)
            return

        self.votes["No"] += 1
        self.bot.active_polls.setdefault(self.poll_message_id, {})[user_id] = "No"

        await interaction.response.edit_message(content=self.get_poll_results(), view=self)

    def get_poll_results(self):
        return f"**Poll Results**\nYes: {self.votes['Yes']}\nNo: {self.votes['No']}"

@bot.tree.command(name="prox3", description="Send an anonymous message, confession, or poll.")
@app_commands.describe(
    message_type="Choose between 'confession', 'message', or 'poll'",
    message="The content of your anonymous message, confession, or poll"
)
@app_commands.choices(
    message_type=[
        app_commands.Choice(name="Confession", value="confession"),
        app_commands.Choice(name="Message", value="message"),
        app_commands.Choice(name="Poll", value="poll"),
    ]
)
async def prox3(interaction: discord.Interaction, message_type: app_commands.Choice[str], message: str):
    channel = interaction.channel

    if message_type.value == "confession":
        await interaction.response.send_message("Your anonymous confession has been sent!", ephemeral=True)

        confession_number = 1
        async for msg in channel.history(limit=100):
            if msg.author == bot.user:
                confession_number = extract_confession_number(msg.content)
                if confession_number > 0:
                    confession_number += 1
                    break

        embed = discord.Embed(
            title=f"Confession #{confession_number}",
            description=message,
            color=discord.Color.dark_blue()
        )

        await channel.send(embed=embed)

    elif message_type.value == "message":
        await interaction.response.send_message("Your anonymous message has been sent!", ephemeral=True)
        await channel.send(message)

    elif message_type.value == "poll":
        await interaction.response.send_message("Your anonymous poll has been created!", ephemeral=True)

        poll_message = await channel.send(f"**Poll:** {message}\nYes: 0\nNo: 0", view=PollView(bot, None))
        poll_view = PollView(bot, poll_message.id)
        poll_message.edit(view=poll_view)

load_dotenv()
token = os.getenv("BOT_TOKEN")
bot.run(token)
