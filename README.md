# Wagerbot (README WIP)
#### VIDEO: _Imagine a video link here_
## Overview
Wagerbot is a Discord bot and website made to handle bets and wagers (with play money) between friends online. Say you want to bet your friend that you could beat them in a 1v1 in CS, or that your player will boot a penalty kick straight into the first row. Whatever it is, Wagerbot has you covered. 

## Use/Commands
When first using Wagerbot, a profile will be automatically created for you with a balance of $1050. When your balance dips below $100, your balance will automatically be set to $100 to allow you to keep playing. Below is a quick rundown of the commands offered by Wagerbot

#### Bot Commands
* `/wager`
Used to offer a wager to someone (mandatory args are member, amount, and a note).
* `/accept`
Used by the person who has been offered the wager to accept and initiate the wager. Note: Once accepted, you can NOT cancel a wager.
* `/decline.`
Used by the person being offered the wager to decline said wager. It can also be used by the person who offered the wager to cancel the wager before it's been accepted.
* `/declare_winner`
Used to declare the winner of a wager and transfer the funds. You can NOT declare yourself the winner.
* `/user_info`
Used to display your account info; it will also provide a link that directs you to a webpage which displays your whole wager history. Note: You can find info for your current pending/ongoing wager.

#### Webpage overview
When visiting https://wagerbot.ca from a browser, you only have access to the homepage, which features a global top 5 leaderboard, the list of Discord commands, a button on the header that links to the project's GitHub page, and a button at the bottom to invite the bot to your server. When using the `/user_info` command, you'll be sent a link in your dm to a page only you may visit, which displays your account's balance, win count, and loss count. Additionally, if you're currently in a pending or ongoing wager, you will be shown information relating to the wager, which includes the amount, your opponent, and a note which the person who created the wager left.

## Deployment 

#### Web App
I've personally chosen to use Python Anywhere for the deployment of this service. The basics of getting it to run included pulling from GitHub into the console provided on the service and installing all the requirements. This was done inside a virtual environment created by following their instructions and finally installing pip and running `pip install -r requirements.txt`. Once done with that, I just had to provide the `app.py`, working directory, and virtual environment location to the Web App page, then finally put in the domain I got from Cloudflare and the Web App was up and running.   

#### Discord Bot
Also running in Python Anywhere, first I had to create a .env file that held the Discord Token (I had pushed my token to GitHub by accident whilst learning how Discord bots work before). After that, it was as simple as writing a bash command that redirects me to my projects directory, enables the virtual environment, and runs `wagerbot.py`. With that command pasted into the Always-On Tasks section of Python Anywhere, Wagerbot was up and running. 

## Source Code and Folders
#### /Static
Holds all the images used in wagerbot.ca and the stylesheet used for the HTML files. 
#### /templates
Holds all the HTML files used for wagerbot.ca. The website uses the Flask framework and Jinja, so all the files extend layout.html and all info is passed from app.py.
* **404.html** Displayed when the user tries to access a non-existent page.
* **layout.html** Holds the metadata, the navbar, and the footer. This website uses Bootstrap for the navbar and all the cards.
* **user.html** Displays the user's basic info (balance, wins, losses) and displays the user's whole wager history.
* **user_wager.html** Same as user.html but also provides a card which holds the information for a user's pending/ongoing wager (opponent, amount, note). App.py checks whether or not there's a pending/ongoing wager and chooses between user.html or user_wager.html to display the user's info.
#### app.py 
Backend for wagerbot.ca. It doesn't have many functions or a lot of code since all of the database handling is offloaded to `dbHelpers.py`. Below are all the routes:
* `@app.route("/")`
  Grabs the global top five using the `dbHelpers.global_top_five` method and returns it to the template `home.html`. You will notice from here on out that a lot of the methods take con and cur as arguments; this is originally due to the database being created and originally accessed in `wager.py`. I later realized I could've just accessed the database from `dbHelpers.py`, but when I tried to fix it, the database would be created without any tables. This has led me to revert to how it was created, and I continued to pass con and cur whenever necessary in any methods. 
* `@app.route("/user/<token>")`
  Each user has a generated token to prevent the user_id from being displayed in the URL bar. When provided a link from wagerbot on Discord, the link will always be formatted as `/user/<token>`. This is to prevent others from being able to see your user history. If a token doesn't exist, the user will be redirected to the error page. If the token provided matches an existing user, the user's ID and wager history are both pulled. Then it checks whether or not the user has any pending or offered wagers and classifies them as such. Depending on whether the user has a pending/ongoing wager or not, `user_wager.html` or `user.html` will be rendered with the current information available.
* `@app.errorhandler(404)`
  Just displays the `404.html` page when a route doesn't exist. 
#### dbHelpers.py
Where all of the reading and writing of `wager.db` occurs. It is the largest file in the project, and all the methods are very self-explanatory. I won't go into all of the methods one by one, but will describe them as we run into them when explaining the rest of the project. 
#### dbinit.py
A very simple script which runs when `wager.py` is run. All it does is check if a database exists; if not, create a database using the schema inside `wager-db.sql`. 
#### requirements.txt
Holds the requirements for this project to run in whichever environment it needs to be deployed in. Just run `pip install -r requirements.txt`.
#### wager-db.sql
This is the schema file for the database. Below are the tables:
* **"wagers"** Holds the wager ID to identify a wager, the Discord server ID where the wager took place, the amount/value of said wager, both users' Discord user IDs (discord_user_id_a or discord_user_id_b), the Discord user ID of the winner, and the status.
* **"servers"** holds the Discord server name and ID. It also holds the token for if I plan to create a server info page which displays server standings.
* **"users"** holds the Discord user ID and username, their balance, wins, and losses, as well as the generated token which is used in `app.py`.
* **"messages"** is a late addition which holds the message created by the wager instigator and the corresponding wager ID.
#### wager.py 
The main Discord bot file. Outside of the basic boilerplate code, you may notice that it runs `init_db()` to create the database. For whatever reason, when setting up con and cursor in the `dbHelpers.py` file, the database would be initialized without a schema. If someone has a fix, please let me know. Besides that, below are the commands for the wagerbot Discord app:
* `/wager` is the command to open a wager and offer it to your chosen opponent. When called, the command will first log both users and the server into the database if not already in it using `dbHelperse.profile_checker`. What `profile_checker` does is check if you exist in the database; if not, it will add you to the database and give you the starting balance of $1050. It also checks if you've changed your username by comparing your current username and the name the database has in relation to your user ID; if it notices a change, it simply updates the username in the database. `server_checker` functions similarly, minus the balance. Then `/wager` checks to make sure all your arguments are valid (not offering a wager to yourself and making sure the amount is a positive integer which you can afford). The method `bet_circumstance` checks if each user has a currently pending/ongoing wager and/or if they have the available balance for the offered wager. Lastly, it uses the `open_wager` method to create a new wager in the database with the status of "Pending" (Note: In the database, "user_id_a" will always be the one who offered the wager).
* `/decline` can be used by the instigator to cancel a wager or by the target to decline the wager. It uses `check_pending`, or `check_pending_offered` depending on whether or not you're the instigator, to see if there is a wager to be declined, then uses `/wager_decline`, which changes the wager status of a user from Pending (Note: users may only have one "Pending" or "Ongoing" wager at a time) to "Declined" and returns a little "receipt" dictionary; this tells the bot whether to send the message that a wager has been declined or cancelled.
* `/accept` changes a "Pending" wager to an "Ongoing" one. It first uses `check_pending` to see if the user has a valid wager offered to them, then uses `wager_accept` to update the wager from "Pending" to "Ongoing. If you read through the `dbHelpers.py` file, you may notice how I've learned to better handle SQL in Python throughout the project. It does start out pretty rough.
* `/declare_winner` completes the wager and transfers the funds from the loser's account to the winner's. (CURRENTLY NOT IMPLEMENTED A WAY TO MAKE SURE BOTH USERS ARE IN THE SAME WAGER)
