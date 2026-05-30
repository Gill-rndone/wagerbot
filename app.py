from flask import Flask, render_template, redirect, request
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


# create users page
@app.route("/user/<token>")
def user(token):
    # grab balance record and username
    user_basic_info = dbHelpers.get_basic(cur, token)
    print(user_basic_info)
    if not user_basic_info:
        return redirect("/404")
    else:
        # grab full player history (output list of dictionaies formated {"server": ,"opponent": ,"wager": ,"outcome": })
        wager_history = dbHelpers.grab_history(con, cur, user_basic_info["username"])

        return render_template("user.html", user=user_basic_info, wagers=wager_history)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
