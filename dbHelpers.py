import sqlite3


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
        cur.execute(
            "INSERT INTO users (discord_user_id, discord_user_name, balance) VALUES(?, ?, ?)",
            (
                user_id,
                user_name,
                base_balance,
            ),
        )
        con.commit()
        print(f"user {user_name} added and initialized to wager.db")
    else:
        print(f"user {user_name} is in database")

    # Check if user has recently changed their username.
    print(f"user_a_history: {user_a_history[0]}")
    if user_a_history[0]:
        if user_a_history != user_name:
            cur.execute(
                "UPDATE users SET discord_user_name = ? WHERE discord_user_id = ?;",
                (user_name, user_id),
            )
            con.commit()
            print(f"username updated for user {user_a_history}")
