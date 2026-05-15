import sqlite3


# Check if user exists in db and initialize if they don't
def profile_checker(con, cur, user_id, user_name):
    # query for if user exists in db
    user_history = cur.execute(
        "SELECT discord_user_name FROM users WHERE discord_user_id = ? ;",
        (user_id,),
    )

    # Initialize user profile in wager.db if not already in there.
    user_a_history = user_history.fetchall()
    if not user_a_history:
        base_balance = 1050
        base_wins_losses = 0
        cur.execute(
            "INSERT INTO users (discord_user_id, discord_user_name, balance, wins, losses) VALUES(?, ?, ?, ?, ?)",
            (user_id, user_name, base_balance, base_wins_losses, base_wins_losses),
        )
        con.commit()
        print(f"user {user_name} added and initialized to wager.db")
    else:
        print(f"user {user_name} is in database")

    # Check if user has recently changed their username.
    if 0 > len(user_a_history):
        print(f"user_a_history: {user_a_history[0]}")
        if user_a_history[0] != user_name:
            cur.execute(
                "UPDATE users SET discord_user_name = ? WHERE discord_user_id = ?;",
                (user_name, user_id),
            )
            con.commit()
            print(f"username updated for user {user_a_history}")


def declare_winner(con, cur, user_id_loser, user_id_winner):
    wager_info = cur.execute(
        "SELECT id, amount FROM wagers WHERE discord_user_id_a = ? OR discord_user_id_b = ? AND status = 'Ongoing'",
        (user_id_loser, user_id_loser),
    ).fetchone()

    wager_id = wager_info[0]
    wager_amount = wager_info[1]

    cur.execute(
        "UPDATE users SET balance = balance + ?, wins = wins + 1 WHERE discord_user_id = ?",
        (
            wager_amount,
            user_id_winner,
        ),
    )
    con.commit()

    cur.execute(
        "UPDATE users SET balance = balance - ?, losses = losses + 1 WHERE discord_user_id = ?",
        (wager_amount, user_id_loser),
    )
    con.commit()

    cur.execute(
        "UPDATE wagers SET winner_discord_user_id = ?, status = 'Resolved' WHERE id = ?",
        (user_id_winner, wager_id),
    )
    con.commit()

    return wager_amount


# Open a wager proposition between two parties.
def wager_open(con, cur, user_a, user_b, amount, server_id):
    default_status = "Pending"
    cur.execute(
        "INSERT INTO wagers (discord_user_id_a, discord_user_id_b, amount, discord_server_id, status) VALUES (?, ?, ?, ?, ?)",
        (
            user_a,
            user_b,
            amount,
            server_id,
            default_status,
        ),
    )
    con.commit()


# check if user has a pending bet OR if they've started the bet that they have pending
def check_pending(con, cur, user_id):
    is_pending = False
    pending_bets = cur.execute(
        "SELECT status FROM wagers WHERE discord_user_id_b = ?", (user_id,)
    )

    for status in pending_bets:
        if status[0] == "Pending":
            is_pending = True

    return is_pending


def check_ongoing(con, cur, user_id):
    is_ongoing = False
    ongoing_bets = cur.execute(
        "SELECT status FROM wagers WHERE discord_user_id_a = ? OR discord_user_id_b = ?",
        (
            user_id,
            user_id,
        ),
    ).fetchall()

    for status in ongoing_bets:
        if status[0] == "Ongoing":
            is_ongoing = True

    return is_ongoing


def wager_decline(con, cur, user_id):
    # Grab info for the wager
    user_id_b = 0
    wager_info_raw = cur.execute(
        "SELECT id, amount, discord_user_id_b, discord_user_id_a FROM wagers WHERE discord_user_id_b = ? OR discord_user_id_a = ? AND status = 'Pending'",
        (user_id, user_id),
    )

    wager_info = wager_info_raw.fetchall()[0]
    wager_id = wager_info[0]
    wager_amount = wager_info[1]

    # Make sure instigator can't be the one to decline the bet
    if wager_info[2] == user_id:
        user_id_b = wager_info[3]
    else:
        user_id_b = wager_info[2]

    # make wager Declined
    cur.execute("UPDATE wagers SET status = 'Declined' WHERE id = ?", (wager_id,))
    con.commit()

    wager_receipt = {"Name": user_id_b, "Amount": wager_amount}
    return wager_receipt


def wager_accept(con, cur, user_id):

    # Grab info for the wager
    user_id_b = 0
    wager_info_raw = cur.execute(
        "SELECT id, amount, discord_user_id_b, discord_user_id_a FROM wagers WHERE discord_user_id_b = ? OR discord_user_id_a = ? AND status = 'Pending'",
        (user_id, user_id),
    )

    wager_info = wager_info_raw.fetchall()[0]
    wager_id = wager_info[0]
    wager_amount = wager_info[1]

    if wager_info[2] == user_id:
        user_id_b = wager_info[3]
    else:
        user_id_b = wager_info[2]

    # make wager Ongoing
    cur.execute("UPDATE wagers SET status = 'Ongoing' WHERE id = ?", (wager_id,))
    con.commit()

    wager_receipt = {"Name": user_id_b, "Amount": wager_amount}
    return wager_receipt


def bet_circumstance(con, cur, user_id_a, user_id_b, amount):
    # check if either user has a pending wager
    validity = True

    if check_pending(con, cur, user_id_a) or check_ongoing(con, cur, user_id_a):
        validity = False
    if check_pending(con, cur, user_id_b) or check_ongoing(con, cur, user_id_b):
        validity = False

    balances = cur.execute(
        "SELECT balance FROM users WHERE discord_user_id IN (?, ?)",
        (user_id_a, user_id_b),
    )

    for balance in balances:
        if balance[0] < amount:
            validity = False

    return validity
