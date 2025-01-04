import discord
from discord import app_commands
import random

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

@bot.tree.command(name="prox3", description="Send an anonymous message.")
async def prox3(interaction: discord.Interaction, message: str):
    
    await interaction.response.send_message("Your anonymous message has been sent!", ephemeral=True)
    
    channel = interaction.channel
    anonymous_id = f"Anon-{random.randint(1000, 9999)}"
    await channel.send(f"Anonymous Message from {anonymous_id}: {message}")


bot.run('thing')
