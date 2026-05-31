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
@tree.command(
    name="wager",
    description="Used to offer a wager someone (mandatory args are member and amount)",
)
async def wager(interaction, member: discord.Member, amount: str, note: str):
    # Check for existing user profiles and create ones where needed.
    dbHelpers.profile_checker(con, cur, interaction.user.id, interaction.user.name)
    dbHelpers.profile_checker(con, cur, member.id, member.name)
    dbHelpers.server_checker(con, cur, interaction.guild.id, interaction.guild.name)
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

    # TODO: make sure to include message and send it to message table
    # initialize wager
    if valid_circumstance:
        # user 'a' will always be instigator (instigator cannot use /accept command)
        print(f"User submitted note of: {note}\n")
        dbHelpers.wager_open(
            con,
            cur,
            interaction.user.id,
            member.id,
            int(amount),
            interaction.guild.id,
            note,
        )
        await interaction.response.send_message(
            f"{member.mention} , a wager of **${amount}** has been offered to you... \n\nYour options are:\n `/decline` or `/accept` to reject or continue the wager.\n{interaction.user.mention}, you can also use the command `/decline` to cancel a wager before it's been accepted.\n\nNOTE: {note}"
        )
    else:
        await interaction.response.send_message(
            "Wager couldn't be processed, at least one of the users either have an insufficient balance, you've input yourself, or they're currently in a pending/ongoing wager."
        )


# decline a wager
@tree.command(
    name="decline",
    description="decline or cancel wager",
)
async def decline(interaction):
    currently_pending = dbHelpers.check_pending(cur, interaction.user.id)

    if currently_pending:
        # change status to declined
        wager_info = dbHelpers.wager_decline(con, cur, interaction.user.id)
        await interaction.response.send_message(
            f"<@{wager_info['Name']}>, your wager of ${wager_info['Amount']} has been declined by {interaction.user.mention}."
        )
    else:
        if dbHelpers.check_pending_offered(cur, interaction.user.id):
            wager_info = dbHelpers.wager_decline(con, cur, interaction.user.id)
            await interaction.response.send_message(
                f"<@{wager_info['Name']}>, your wager of ${wager_info['Amount']} has been cancelled."
            )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} , you currently don't have any pending wagers offered to you"
            )


# accept a wager
@tree.command(
    name="accept",
    description="accept wager",
)
async def accept(interaction):
    # check if user has a currently pending wager
    currently_pending = dbHelpers.check_pending(cur, interaction.user.id)

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
@tree.command(
    name="declare_winner",
    description="declare opponent as winner",
)
async def declare_winner(interaction, member: discord.Member):
    currently_ongoing = dbHelpers.check_ongoing(cur, interaction.user.id)

    # fix: forgot to add this earlier leading to the ability to send money to anyone
    if currently_ongoing:
        currently_ongoing = dbHelpers.check_ongoing(cur, member.id)

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


@tree.command(name="user_info", description="Display user info and link to user page")
async def user_info(interaction):
    dbHelpers.profile_checker(con, cur, interaction.user.id, interaction.user.name)
    # grab token
    url_token = dbHelpers.grab_token(cur, interaction.user.id)

    # TODO: make sure to change before deployment
    local_test = "http://127.0.0.1:5000"
    deploy = "https://wagerbot.ca"
    user_link = f"{deploy}/user/{url_token}"

    basic_info = dbHelpers.get_basic(cur, url_token)

    overview = f"## Acount Info\n**Account Balance:** {basic_info['balance']}\n**Wins:** {basic_info['wins']}\n**Losses:** {basic_info['losses']}\n"

    user_id = interaction.user.id
    wager_line = None
    has_wager = False

    if (
        dbHelpers.check_ongoing(cur, user_id)
        or dbHelpers.check_pending(cur, user_id)
        or dbHelpers.check_pending_offered(cur, user_id)
    ):
        current_wager = dbHelpers.current_wager(cur, user_id)

        status = None

        has_wager = True

        if dbHelpers.check_ongoing(cur, user_id):
            status = "Ongoing"
        else:
            status = "Pending"

        wager_line = f"You have a current wager from {current_wager['opponent']}\n**Amount**: {current_wager['amount']}\n**Status**: {status}\n**Note**: {current_wager['note']}\n"

    print(f"generated link: {user_link}")

    if has_wager:
        await interaction.response.send_message(
            f"{overview}\n{wager_line}\nFor more info click [**Here**]({user_link})"
        )
    else:
        await interaction.response.send_message(
            f"{overview}\nFor more info click [**Here**]({user_link})"
        )


client.run(token, log_handler=handler, log_level=logging.DEBUG)
