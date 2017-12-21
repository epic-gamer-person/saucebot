#!/usr/bin/python
from Naked.toolshed.shell import muterun_js
import sys
import praw
import re
import os
import json
import pickle
import threading
import atexit
import Queue
import traceback

from message import Message

class Bot:

  def __init__(self):
    self.ratelimit = 600

    self.log = list()
    self.event = threading.Event()
    self.queue = Queue.Queue()
    self.load_reply_history()
    atexit.register(self.exit)

  def load_reply_history(self):
    if not os.path.isfile("reply_history.p"):
      self.log.append(Message("m", "Generating new reply history."))
      self.reply_history = dict()
      self.log.append(Message("m", "New reply history generated."))
    else:
      with open("reply_history.p", "rb") as f:
        self.log.append(Message("m", "Loading reply history."))
        self.reply_history = pickle.load(f)
        self.log.append(Message("m","Reply history loaded."))

  def save_reply_history(self):
    with open("reply_history.p", "wb") as f:
      self.log.append(Message("m", "Saving reply history."))
      pickle.dump(self.reply_history, f, pickle.HIGHEST_PROTOCOL)
      self.log.append(Message("m", "Reply history saved."))

  def scan_comments(self):
    reddit = praw.Reddit('sauce_bot')
    # edit the string to desired subreddits
    subreddit = reddit.subreddit("konchadesu+anime_irl")
    scan_history = dict()
    for comment in subreddit.stream.comments(pause_after=0):
      if self.event.is_set():
        break;
      if comment is None:
        continue
      contains_re = re.search("(sauce|source)\\?", comment.body, re.IGNORECASE)
      top_level_comment = comment.parent_id == comment.link_id
      new_submission = scan_history.get(comment.submission.id) is None
      if contains_re and top_level_comment and new_submission:
        self.queue.put(comment)
        scan_history[comment.submission.id] = True
        self.log.append(Message("s", "Scan process added comment to queue!"))

  def reply_to_comments(self):
    while not self.event.is_set():
      comment = self.queue.get(block=True, timeout=None)
      if comment is not None:
        self.log.append(Message("r", "Reply process handling next comment."))
        new_submission = self.reply_history.get(comment.submission.id) is None
        if new_submission:
          self.log.append(Message("v", comment.body))
          self.log.append(Message("r", "Reply process querying saucenao..."))
          response = muterun_js('sauce.js', comment.submission.url) # run script to call saucenao api
          if response.exitcode == 0:
            if response.stdout != "\n": # possible matches
              self.log.append(Message("v", response.stdout))
              reply = self.build_reply(response)
              self.log.append(Message("v", reply))
              comment.reply(reply)
              self.reply_history[comment.submission.id] = True
              self.log.append(Message("r", "Reply process sent reply with possible matches!"))
              self.log.append(Message("r", "Reply process now sleeping for " + str(self.ratelimit) + " seconds."))
              self.event.wait(timeout=self.ratelimit)
            else:
              self.reply_history[comment.submission.id] = True
              self.log.append(Message("r", "Reply process dropped comment with no matches."))
          else:
            sys.stderr.write(response.stderr)
        else:
          self.log.append(Message("r", "Reply process dropped previously processed comment."))

  def run(self):
    self.scan_thread = threading.Thread(target=self.scan_comments)
    self.scan_thread.start()
    self.reply_thread = threading.Thread(target=self.reply_to_comments)
    self.reply_thread.start()
    try:
      while True:
        r = raw_input()
        self.execute(r)
    except:
      traceback.print_exc()
      self.event.set()
      self.queue.put(None) # dummy value to unblock reply_thread waiting on queue
      self.scan_thread.join()
      self.reply_thread.join()

  def execute(self, r):
    if r == "p":
      for line in self.log:
        print(line.__repr__())

  def exit(self):
    if len(self.reply_history) > 0:
      self.save_reply_history()

  def build_reply(self, response):
    reply = """Possible matches from [SauceNAO](https://saucenao.com/)\n\nNSFW Rating|Site|URL|Similarity\n-|-|-|-\n"""
    li = json.loads(response.stdout)
    for di in li:
      rating = {0:"UKNOWN", 1:"SAFE", 2:"QUESTIONABLE", 3:"NSFW"}.get(di.get("rating"))
      reply += rating + "|" + di.get("site") + "|" + di.get("url") + "|" + str(di.get("similarity")) + "\n"
    reply += "\n---\nHello, I am a bot!"
    return reply

if __name__ == '__main__':
  Bot().run()
