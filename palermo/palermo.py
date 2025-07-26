import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import datetime
import asyncio
import pyttsx3
import os


TOKEN = ""
GUILD_ID =   

intents = discord.Intents.all()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

roles = []

@tree.command(name="palermo_start", description="Ξεκίνα ένα παιχνίδι Wordle", guild=discord.Object(id=GUILD_ID))
async def start_wordle(interaction: discord.Interaction):
    user_id = interaction.user.id
    await interaction.response.send_message(
        "🎯 Ξεκίνησε νέο Palermo!"
    )
