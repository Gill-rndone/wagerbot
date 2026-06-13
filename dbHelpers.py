import secrets


def server_checker(con, cur, server_id, server_name):
    server_history = cur.execute(
        "SELECT discord_server_name FROM servers WHERE discord_server_id = ?",
        (server_id,),
    ).fetchone()

    if not server_history:
        server_token = secrets.token_urlsafe(16)
        cur.execute(
            "INSERT INTO servers (discord_server_id, discord_server_name, token) VALUES(?, ?, ?)",
            (server_id, server_name, server_token),
        )
        con.commit()
        print(f"{server_name} has been added to wager.db")
    else:
        if server_history[0] != server_name:
            cur.execute(
                "UPDATE servers SET discord_server_name = ? WHERE discord_server_id = ?",
                (server_name, server_id),
            )
            con.commit()
            print(f"{server_name} has had it's username updated")
        else:
            print(f"{server_name} already in wager.db")


# Check if user exists in db and initialize if they don't
def profile_checker(con, cur, user_id, user_name):
    # query for if user exists in db
    user_history = cur.execute(
        "SELECT discord_user_name FROM users WHERE discord_user_id = ? ;", (user_id,)
    )

    # Initialize user profile in wager.db if not already in there.
    user_a_history = user_history.fetchall()
    if not user_a_history:
        base_balance = 1050
        base_wins_losses = 0
        token = secrets.token_urlsafe(16)
        cur.execute(
            "INSERT INTO users (discord_user_id, discord_user_name, balance, wins, losses, token) VALUES(?, ?, ?, ?, ?, ?)",
            (
                user_id,
                user_name,
                base_balance,
                base_wins_losses,
                base_wins_losses,
                token,
            ),
        )
        con.commit()
        print(f"user {user_name} added and initialized to wager.db")
    else:
        # check if balance less than $100
        balance = cur.execute(
            "SELECT balance FROM users WHERE discord_user_id = ?", (user_id,)
        ).fetchone()[0]
        print(f"user balance = ${balance}")
        if int(balance) < 100:
            cur.execute(
                "UPDATE users SET balance = 100 WHERE discord_user_id = ?", (user_id,)
            )
            con.commit()

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

        print(f"user {user_name} is in database")


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
def wager_open(con, cur, user_a, user_b, amount, server_id, message):
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

    wager_id = cur.execute(
        "SELECT id FROM wagers WHERE discord_user_id_a = ? AND discord_user_id_b = ? AND amount = ? AND discord_server_id = ? AND status = ?",
        (user_a, user_b, amount, server_id, default_status),
    ).fetchone()[0]

    cur.execute(
        "INSERT INTO messages (wager_id, message_content) VALUES (?, ?)",
        (wager_id, message),
    )
    con.commit()


# check if user has a pending bet OR if they've started the bet that they have pending
def check_pending(cur, user_id):
    is_pending = False
    pending_bets = cur.execute(
        "SELECT status FROM wagers WHERE discord_user_id_b = ?", (user_id,)
    )

    for status in pending_bets:
        if status[0] == "Pending":
            is_pending = True

    return is_pending


def check_pending_offered(cur, user_id):
    is_pending = False
    pending_bets = cur.execute(
        "SELECT status FROM wagers WHERE discord_user_id_a = ?", (user_id,)
    )

    for status in pending_bets:
        if status[0] == "Pending":
            is_pending = True

    return is_pending


def check_ongoing(cur, user_id):
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

def check_match(cur, user_id_a, user_id_b):
    is_match = False
    ongoing_bets_a = cur.execute(
            "SELECT id FROM wagers WHERE discord_user_id_a = ? or discord_user_id_b = ? AND status = 'Ongoing'", (user_id_a, user_id_a)).fetchone()[0]
    ongoing_bets_a = cur.execute(
            "SELECT id FROM wagers WHERE discord_user_id_a = ? or discord_user_id_b = ? AND status = 'Ongoing'", (user_id_b, user_id_b)).fetchone()[0]
    if ongoing_bets_a == ongoing_bets_a:
        is_match = True
        print("wagers are a match")

    return is_match


def wager_decline(con, cur, user_id):
    # Grab info for the wager
    user_id_b = 0
    wager_info = cur.execute(
        "SELECT id, amount, discord_user_id_b, discord_user_id_a FROM wagers WHERE discord_user_id_b = ? OR discord_user_id_a = ? AND status = 'Pending'",
        (user_id, user_id),
    ).fetchall()[0]

    wager_id = wager_info[0]
    wager_amount = wager_info[1]

    print(f"decling wager of id: {wager_id}")

    # identify whether wager is being declined or cancelled
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


def global_top_five(con, cur):
    # GRAB TOP 5 USER NAME AND BALNCE
    global_top_five = cur.execute(
        "SELECT discord_user_name, balance, discord_user_id FROM users ORDER BY balance DESC LIMIT 5;"
    ).fetchall()

    global_top_five_formatted = []

    for position, user in enumerate(global_top_five):
        position += 1
        user_id = user[2]
        username = user[0]
        balance = f"${user[1]}"
        profile_checker(con, cur, user_id, username)
        print(f"position: {position} | balance: ${balance} | name: ${username}")
        user_row = {
            "position": str(position),
            "username": username,
            "balance": balance,
            "user_id": user_id,
        }
        global_top_five_formatted.append(user_row)
    # testing
    for row in global_top_five_formatted:
        print(row)
    return global_top_five_formatted
    # RETURN AS LIST OF DICTIONARIES


def bet_circumstance(con, cur, user_id_a, user_id_b, amount):
    # check if either user has a pending wager
    validity = True

    if check_pending(cur, user_id_a) or check_ongoing(cur, user_id_a):
        validity = False
    if check_pending(cur, user_id_b) or check_ongoing(cur, user_id_b):
        validity = False

    balances = cur.execute(
        "SELECT balance FROM users WHERE discord_user_id IN (?, ?)",
        (user_id_a, user_id_b),
    ).fetchall()

    for balance in balances:
        if balance[0] < amount:
            validity = False

    # also forgot to check fo this
    if user_id_a == user_id_b:
        validity = False

    return validity


def get_basic(cur, token):
    basic_info_raw = cur.execute(
        "SELECT discord_user_name, balance, wins, losses FROM users WHERE token = ?",
        (token,),
    ).fetchall()
    if not basic_info_raw:
        return None
    else:
        basic_info = basic_info_raw[0]
        balance_formatted = f"${basic_info[1]}"
        info_dict = {
            "username": basic_info[0],
            "balance": balance_formatted,
            "wins": basic_info[2],
            "losses": basic_info[3],
        }
        return info_dict


def grab_history(con, cur, username):
    # grab user_id
    user_id = cur.execute(
        "SELECT discord_user_id FROM users WHERE discord_user_name = ?", (username,)
    ).fetchone()[0]

    profile_checker(con, cur, user_id, username)

    # grab all resolved wagers the user has been apart of
    history = cur.execute(
        "SELECT discord_server_id, amount, discord_user_id_a, discord_user_id_b, winner_discord_user_id FROM wagers WHERE status = 'Resolved' AND discord_user_id_a = ? OR discord_user_id_b = ?",
        (user_id, user_id),
    ).fetchall()

    # construct list of dictionaries including the necessary data from history
    history_dict = []
    for index, wager_index in enumerate(history):
        server_id = wager_index[0]
        wager = wager_index[1]
        user_a_id = wager_index[2]
        user_b_id = wager_index[3]
        winner_id = wager_index[4]
        server = cur.execute(
            "SELECT discord_server_name FROM servers WHERE discord_server_id = ?",
            (server_id,),
        ).fetchone()[0]

        opponent_id = 0

        if user_id == user_a_id:
            opponent_id = user_b_id
        else:
            opponent_id = user_a_id
        opponent = cur.execute(
            "SELECT discord_user_name FROM users WHERE discord_user_id = ?",
            (opponent_id,),
        ).fetchone()[0]

        wager_formatted = f"${wager}"

        outcome = None
        if winner_id == user_id:
            outcome = "Win"
        else:
            outcome = "Loss"

        wager_row = {
            "server": server,
            "opponent": opponent,
            "wager": wager_formatted,
            "outcome": outcome,
        }
        print(f"wager {index + 1} accounted for: {wager_row}")
        history_dict.append(wager_row)

    return history_dict


def grab_token(cur, user_id):
    token = cur.execute(
        "SELECT token FROM users WHERE discord_user_id = ?", (user_id,)
    ).fetchone()[0]
    return token


def token_to_id(cur, token):
    user_id = cur.execute(
        "SELECT discord_user_id FROM users WHERE token = ?", (token,)
    ).fetchone()[0]

    return user_id


def current_wager(cur, user_id):
    wager_info = cur.execute(
        "SELECT id, amount, discord_user_id_a, discord_user_id_b FROM wagers WHERE (status = 'Pending' OR status = 'Ongoing') AND (discord_user_id_a = ? OR discord_user_id_b = ?)",
        (user_id, user_id),
    ).fetchone()
    # TODO: Format wager info into a dictionary.

    wager_id = wager_info[0]
    wager_amount = wager_info[1]
    user_id_a = wager_info[2]
    user_id_b = wager_info[3]

    opponent_id = 0
    if user_id == user_id_b:
        opponent_id = user_id_a
    else:
        opponent_id = user_id_b

    opponent_name = cur.execute(
        "SELECT discord_user_name FROM users WHERE discord_user_id = ?", (opponent_id,)
    ).fetchone()[0]

    wager_message = cur.execute(
        "SELECT message_content FROM messages WHERE wager_id = ?", (wager_id,)
    ).fetchone()[0]

    wager_info = {
        "amount": f"${wager_amount}",
        "note": wager_message,
        "opponent": opponent_name,
    }

    return wager_info
