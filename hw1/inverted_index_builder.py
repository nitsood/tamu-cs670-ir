import re
import os
import pickle
from collections import defaultdict

filenames = []
inverted_index = defaultdict(set)

def tokenize(text):
  p = re.compile(r'\W+')
  return p.split(text)

def read_file(filename):
  f = open(filename, 'r')
  st = f.read()
  f.close()
  return st

def build_inverted_index(dir_name):
  unix_cmd = 'ls {0} | sort -n'.format(dir_name)
  p = os.popen(unix_cmd)
  filenames = p.readlines()
  for i in range(0, len(filenames)):
    filename = filenames[i] 
    file_contents = read_file(dir_name+filename[:-1])
    file_contents = re.sub(r'_', '', file_contents)
    tokens = tokenize(file_contents)
    add_to_index(tokens, int(filename.split('.')[0]))
  return inverted_index

def add_to_index(word_list, posting):
  for i in range(0, len(word_list)):
    word = word_list[i].lower()
    if(word is None or word == ''):
      continue
    inverted_index[word].add(posting)
  return

def write_index(index):
  f = open('inv_index.pick', 'wb')
  pickle.dump(index, f)
  f.close()
  print 'Index pickled to file inv_index.pick'
  return

