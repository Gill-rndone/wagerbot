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
* `/decline`
Used by the person being offered the wager to decline said wager. It can also be used by the person who offered the wager to cancel the wager before it's been accepted.
* `/declare_winner`
Used to declare the winner of a wager and transfer the funds. You can NOT declare yourself the winner.
* `/user_info`
Used to display your account info, it will also provide a link that directs you to a webpage which displays your whole wager history. Note: You can find info for your current pending/ongoing wager.

#### Webpage overview
When visiting https://wagerbot.ca from a browser, you only have access to the homepage, which features a global top 5 leaderboard, the list of Discord commands, a button on the header that links to the project's GitHub page, and a button at the bottom to invite the bot to your server. When using the `/user_info` command, you'll be sent a link in your dm to a page only you may visit, which displays your account's balance, win count, and loss count. Additionally, if you're currently in a pending or ongoing wager, you will be shown information relating to the wager, which includes the amount, your opponent, and a note which the person who created the wager left.

## Deployment 

#### Web App
I've personally chosen to use Python Anywhere for the deployment of this service. The basics of getting it to run included pulling from GitHub into the console provided on the service and installing all the requirements. This was done inside a virtual environment created by following their instructions and finally installing pip and running `pip install -r requirements.txt`. Once done with that, I just had to provide the `app.py`, working directory, and virtual environment location to the Web App page, then finally put in the domain I got from Cloudflare and the Web App was up and running.   

#### Discord Bot
Also running in Python Anywhere, first I had to create a .env file that held the Discord Token (I had pushed my token to GitHub by accident whilst learning how Discord bots work before). After that, it was as simple as writing a bash command that redirects me to my projects directory, enables the virtual environment, and runs `wagerbot.py`. With that command pasted into the Always-On Tasks section of Python Anywhere, Wagerbot was up and running. 

