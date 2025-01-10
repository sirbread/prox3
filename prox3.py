import discord
from discord import app_commands
import re
import os
from dotenv import load_dotenv

class AnonymousMessageBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

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

@bot.tree.command(name="prox3", description="Send an anonymous message or confession.")
@app_commands.describe(
    message_type="Choose between 'confession' or 'message'",
    message="The content of your anonymous message or confession"
)
@app_commands.choices(
    message_type=[
        app_commands.Choice(name="Confession", value="confession"),
        app_commands.Choice(name="Message", value="message"),
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

        await channel.send(f"Confession #{confession_number}: {message}")

    elif message_type.value == "message":
        await interaction.response.send_message("Your anonymous message has been sent!", ephemeral=True)
        await channel.send(message)

load_dotenv()
token = os.getenv("BOT_TOKEN")
bot.run(token)
