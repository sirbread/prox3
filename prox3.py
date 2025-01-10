import discord
from discord import app_commands
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

load_dotenv()
token = os.getenv("BOT_TOKEN")
bot.run(token)
