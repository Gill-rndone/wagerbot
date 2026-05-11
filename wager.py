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

# open a wager
@tree.command(name="wager")
async def wager(interaction, member: discord.Member, amount: str):
    # Check for existing user profiles and create ones where needed.
    dbHelpers.profile_checker(con, cur, interaction.user.id, interaction.user.name)
    dbHelpers.profile_checker(con, cur, member.id, member.name)
    
    valid_circumstance = True

    # Make sure value is an integer
    try:
        amount = int(amount)
    except ValueError:
        await interaction.response.send_message("Sorry, all wager amounts must be a valid integer... (No decimals, letters, or negatives)")
        print("invalid input for amount argument")
        valid_circumstance = False
        
    
    if int(amount) < 1:
        await interaction.response.send_message("Sorry, all wager amounts must be a valid integer... (No decimals, letters, or negatives)")
        print("invalid input for amount argument")
        valid_circumstance = False

    # Check if both users have the valid minimum balance and are not currently in a prending wager.
    valid_circumstance = dbHelpers.bet_circumstance(con, cur, member.id, interaction.user.id, amount)

    # initialize wager 
    if valid_circumstance == True:
        dbHelpers.wager_open(con, cur, interaction.user.id, member.id, int(amount), interaction.guild.id)
        await interaction.response.send_message(f"@{member.name}, a wager of {amount} wager points has been offered to you... \n\nYour options are:\n `/decline` or `/accept` to reject or continue the wager.\n`/raise` (amount) to raise your wager by the input ammount.\n `/lower` (amount) to lower the wager by the input ammount (minimum must be greater than 0)")
    else:
        await interaction.response.send_message(f"Wager couldn't be processed, at least one of the users either have an insufficient balance or they're currently in a pending wager.")


client.run(token, log_handler=handler, log_level=logging.DEBUG)
