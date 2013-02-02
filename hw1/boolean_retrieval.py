import sys
import re
import os
import pickle
from collections import defaultdict

filenames = []
file_ctr = 0
#inverted_index = {}
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
    tokens = tokenize(read_file(dir_name+filename[:-1]))
    add_to_index(tokens, int(filename.split('.')[0]))
  return

def add_to_index(word_list, posting):
  for i in range(0, len(word_list)):
    word = word_list[i].lower()
    if(word is None or word == ''):
      continue
    inverted_index[word].add(posting)
    #postings = set([])
    #if(word in inverted_index):
    #  postings = inverted_index.get(word)
    #postings.add(posting)
    #inverted_index[word] = postings
  return

def write_index():
  f = open('index.txt', 'w')
  pickle.dump(inverted_index, f)
  #n = 'Total keys: {0}\n'.format(len(inverted_index))
  #for key in sorted(inverted_index.keys()):
  #  n += key+" = {0}\n".format(inverted_index.get(key))
  #f.write(n)
  f.close()
  print 'Index written to file index.txt'
  return

def find(query):
  words = query.split()
  if(len(words) == 1):
    print_set(inverted_index.get(words[0]))
    return
  postings = []
  for i in range(0, len(words)):
    word = words[i].lower()
    if(word not in inverted_index):
      print_set(None)
      return
    else:
      postings.append(inverted_index.get(word))
  result = set(postings[0]).intersection(*postings[1:])
  print_set(result)
  return

def print_set(s):
  if(s is not None and len(s) != 0):
    for p in s:
      print '{0} '.format(p),
    print
  else:
    print 'No match'
  return

def main():
  st = build_inverted_index('books/books/')
  write_index()
  #prompt = '>>'
  #while(True):
  #  print prompt,
  #  query = raw_input()
  #  if(query == 'q' or query == 'Q'):
  #    print '\nCiao\n'
  #    break
  #  find(query)
  return

if __name__ == '__main__':
  sys.exit(main())
