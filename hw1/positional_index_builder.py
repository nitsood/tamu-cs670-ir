import re
import os
import pickle
from collections import defaultdict
from collections import OrderedDict

def no_use():
  """one liner used only for defaultdict's declaration.
  Could have used lambda but then lambda doesn't pickle"""
  return defaultdict(list)

filenames = []
positional_index = defaultdict(no_use)

def tokenize(text):
  p = re.compile(r'\W+')
  return p.split(text)

def read_file(filename):
  f = open(filename, 'r')
  st = f.read()
  f.close()
  return st

def build_positional_index(dir_name):
  unix_cmd = 'ls {0} | sort -n'.format(dir_name)
  p = os.popen(unix_cmd)
  filenames = p.readlines()
  for filename in filenames: 
    file_contents = read_file(dir_name+filename[:-1])
    file_contents = re.sub(r'_', '', file_contents)
    tokens = tokenize(file_contents)
    add_to_index(tokens, int(filename.split('.')[0]))
  return positional_index

def add_to_index(word_list, posting):
  for i in range(0, len(word_list)):
    word = word_list[i].lower()
    if(word is None or word == ''):
      continue
    positional_index[word][posting].append(i)  ##plain awesome
  return

def write_index(index):
  f = open('pos_index.pick', 'wb')
  pickle.dump(index, f)
  f.close()
  print 'Index pickled to file pos_index.pick'
  return

