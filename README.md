Saucebot
---
Reddit bot that responds to comments asking for sauce(source) on specific subreddits.

### Setup
1. run ```npm install``` and ```pip install -r requirements.txt``` to install dependencies
2. edit the empty fields in praw.ini to contain your [client_id, client_secret](https://github.com/reddit/reddit/wiki/OAuth2), password, and username
3. edit the list of subreddits on line 49 of bot.py to the subreddits your bot will monitor
### Run
run ```python bot.py```
when running, enter p to print log
