import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import sqlite3
import os
from dbinit import init_db
import dbHelpers
import secrets

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
        await interaction.response.send_message(
            "Sorry, all wager amounts must be a valid integer... (No decimals, letters, or negatives)"
        )
        print("invalid input for amount argument")
        valid_circumstance = False

    if int(amount) < 1:
        await interaction.response.send_message(
            "Sorry, all wager amounts must be a valid integer... (No decimals, letters, or negatives)"
        )
        print("invalid input for amount argument")
        valid_circumstance = False

    # Check if both users have the valid minimum balance and are not currently in a prending wager.
    valid_circumstance = dbHelpers.bet_circumstance(
        con, cur, member.id, interaction.user.id, amount
    )

    # initialize wager
    if valid_circumstance == True:
        # user 'a' will always be instigator (instigator cannot use /accept command)
        dbHelpers.wager_open(
            con, cur, interaction.user.id, member.id, int(amount), interaction.guild.id
        )
        await interaction.response.send_message(
            f"{member.mention} , a wager of ${amount} has been offered to you... \n\nYour options are:\n `/decline` or `/accept` to reject or continue the wager."
        )
    else:
        await interaction.response.send_message(
            f"Wager couldn't be processed, at least one of the users either have an insufficient balance or they're currently in a pending/ongoing wager."
        )


# decline a wager
@tree.command(name="decline")
async def decline(interaction):
    currently_pending = dbHelpers.check_pending(con, cur, interaction.user.id)
    user_name = interaction.user.name

    if currently_pending:
        # change status to declined
        wager_info = dbHelpers.wager_decline(con, cur, interaction.user.id)
        await interaction.response.send_message(
            f"<@{wager_info['Name']}>, your wager of ${wager_info['Amount']} has been declined by {interaction.user.mention}."
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.mention} , you currently don't have any pending wagers offered to you"
        )


# accept a wager
@tree.command(name="accept")
async def accept(interaction):
    # check if user has a currently pending wager
    currently_pending = dbHelpers.check_pending(con, cur, interaction.user.id)
    user_name = interaction.user.name

    if currently_pending:
        # change status to ongoing
        wager_info = dbHelpers.wager_accept(con, cur, interaction.user.id)
        await interaction.response.send_message(
            f"<@{wager_info['Name']}>, Your wager of ${wager_info['Amount']} has been accepted.\nThe `/declare_winner` command is now available to both users. Remember, you cannot declare yourself the winner."
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.mention} , you currently don't have any pending wagers offered to you"
        )


# declare the wager winner and complete transaction.
@tree.command(name="declare_winner")
async def accept(interaction, member: discord.Member):
    currently_ongoing = dbHelpers.check_ongoing(con, cur, interaction.user.id)

    if not currently_ongoing:
        await interaction.response.send_message(
            f"{interaction.user.mention}, you're not currently in an ongoing wager."
        )
    else:
        if interaction.user.id == member.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}, You cannot declare yourself the winner of a wager"
            )
        else:
            wager_amount = dbHelpers.declare_winner(
                con, cur, interaction.user.id, member.id
            )
            await interaction.response.send_message(
                f"{interaction.user.mention}, your wager of ${wager_amount} has successfully been paid off to {member.mention}"
            )


client.run(token, log_handler=handler, log_level=logging.DEBUG)
