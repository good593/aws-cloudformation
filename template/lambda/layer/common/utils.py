import os

def do_mkdir(path):
  if not os.path.exists(path):
    os.mkdir(path)
