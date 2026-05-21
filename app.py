from flask import Flask, render_template
import dbHelpers 

app = Flask(__name__)


@app.route("/")
def home():
    global_top_ten = [{"position": 1,"username": charlie,"balance": "$65"}, {"position": 2, "username": "bob", "balance": "$35"}, {"position": 3, "username": "steve", "balance": "$10"}]
    return render_template("home.html", global_top_ten = global_top_ten)

