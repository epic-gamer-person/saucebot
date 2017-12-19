#!/usr/bin/python
from Naked.toolshed.shell import muterun_js
import praw
import re
import os
import sys
import json
import pickle
import sys
import signal

class Bot:

  def __init__(self):
    self.kill_flag = False
    signal.signal(signal.SIGINT, self.exit)
    signal.signal(signal.SIGTERM, self.exit)

  def load_history(self):
    if not os.path.isfile("history.p"):
      print("Generating new history.")
      self.history = dict()
      print("New history generated.")
    else:
      with open("history.p", "rb") as f:
        print("Loading history.")
        self.history = pickle.load(f)
        print("History loaded.")

  def save_history(self):
    with open("history.p", "wb") as f:
      print("Saving history.")
      pickle.dump(self.history, f, pickle.HIGHEST_PROTOCOL)
      print("History saved.")

  def run(self):
    reddit = praw.Reddit('sauce_bot')
    # edit the string to desired subreddits
    subreddit = reddit.subreddit("konchadesu+traaaaaaannnnnnnnnns+whataweeb+animenocontext+animefunny")

    self.load_history()

    try:
      for comment in subreddit.stream.comments(pause_after=0):
        if self.kill_flag == True:
          print("Shutting down.")
          break;
        if comment is None:
          sys.stdout.write(".")
          sys.stdout.flush()
          continue
        else:
          sys.stdout.write("!")
          sys.stdout.flush()
        contains_re = re.search("(sauce|source)\\?", comment.body, re.IGNORECASE)
        top_level_comment = comment.parent_id == comment.link_id
        new_comment = self.history.get(comment.submission.id) is None

        if contains_re and top_level_comment and new_comment:
          self.history[comment.submission.id] = True
          print("\n" + comment.body)
          response = muterun_js('sauce.js', comment.submission.url) # run script to call saucenao api
          if response.exitcode == 0:
            if response.stdout != "\n":
              reply = self.build_reply(response)
              print(reply)
              comment.reply(reply)
              print("Sent reply!")
            else:
              print("No matches.")
          else:
            sys.stderr.write(response.stderror)
    except Exception as e:
      print(e)
    
    self.save_history()
   
  def build_reply(self, response):
    reply = """Possible matches from [SauceNAO](https://saucenao.com/)\n\nNSFW Rating|Site|URL|Similarity\n-|-|-|-\n"""
    li = json.loads(response.stdout)
    for di in li:
      rating = {0:"UKNOWN", 1:"SAFE", 2:"QUESTIONABLE", 3:"NSFW"}.get(di.get("rating"))
      reply += rating + "|" + di.get("site") + "|" + di.get("url") + "|" + str(di.get("similarity")) + "\n"
    reply += "\\n---\nHello, I am a bot and you are a cute!"
    return reply

  def exit(self, signum, frame):
    self.kill_flag = True

if __name__ == '__main__':
  Bot().run()
