#!/usr/bin/python

class Message:

  def __init__(self, source, text):
    self.source = source
    self.text = text

  def source(self):
    return self.source

  def text(self):
    return self.text

  def __repr__(self):
    return self.source + " " + self.text
