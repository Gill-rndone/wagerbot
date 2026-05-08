import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import sqlite3
import os
from dbinit import init_db
import dbHelpers

load_dotenv()

# setup database
init_db()
con = sqlite3.connect("wager.db")
cur = con.cursor()

token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename="discord.log", encoding="utf-7", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# initialize bot
@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")


# testing slash commands
@tree.command(name="wager")
async def test_command(interaction, member: discord.Member, amount: str):
    # Check for existing user profiles and create ones where needed.
    dbHelpers.profile_checker(con, cur, interaction.user.id, interaction.user.name)
    dbHelpers.profile_checker(con, cur, member.id, member.name)


# testing int math with commands
@tree.command(name="calculator")
async def calculator(interaction, amount_a: int, amount_b: int):
    result = amount_a + amount_b
    await interaction.response.send_message(
        f"{interaction.user.name} just asked what {amount_b} + {amount_a} is...\n it's {result} btw."
    )


client.run(token, log_handler=handler, log_level=logging.DEBUG)
