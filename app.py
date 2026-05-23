from flask import Flask, render_template, redirect, url_for
import dbHelpers
import sqlite3


app = Flask(__name__)

# ngl I realized way too late I could've just added con and cur to the dbHelpers..
# but it's too late so I'm just going to keep passing it into everymethod because I'm tired.
con = sqlite3.connect("wager.db", check_same_thread=False)
cur = con.cursor()


@app.route("/")
def home():
    # grab top FIVE users based on balance
    global_top_five = dbHelpers.global_top_five(con, cur)
    return render_template("home.html", global_top_five=global_top_five)


# TODO: create users page
@app.route("/user/<token>")
def user(token):
    user_basic_info = dbHelpers.get_basic(con, cur, token)
    print(user_basic_info)
    if not user_basic_info:
        return redirect("/")
    else:
        return render_template("user.html", user=user_basic_info)
