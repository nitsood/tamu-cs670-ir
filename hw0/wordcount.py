#/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/


import sys

# +++your code here+++
# Define print_words(filename) and print_top(filename) functions.
# You could write a helper utility function that reads a file
# and builds and returns a word/count dict for it.
# Then print_words() and print_top() can just call the utility function.

def print_words(filename):
  word_dict = find_count(filename)
  for key in sorted(word_dict.keys()):
    print key+" "+str(word_dict[key])
  return 

def print_top(filename):
  word_dict = find_count(filename)
  ctr = 0
  for key in sorted(word_dict, key=word_dict.get, reverse=True):
    print key+" "+str(word_dict[key])
    ctr += 1
    if(ctr == 20):
      break
  return 

def find_count(filename):
  file_contents = read_file(filename)
  wordlist = file_contents.split()
  word_dict = {}
  for i in range(0, len(wordlist)):
    word = wordlist[i].lower()
    val = 1
    if(word in word_dict):
      val = word_dict[word]
      val += 1
    word_dict[word] = val
  return word_dict

def read_file(filename):
  f = open(filename, 'r')
  st = f.read()
  f.close()
  return st

###

# This basic command line argument parsing code is provided and
# calls the print_words() and print_top() functions which you must define.
def main():
  if len(sys.argv) != 3:
    print 'usage: ./wordcount.py {--count | --topcount} file'
    sys.exit(1)

  option = sys.argv[1]
  filename = sys.argv[2]
  if option == '--count':
    print_words(filename)
  elif option == '--topcount':
    print_top(filename)
  else:
    print 'unknown option: ' + option
    sys.exit(1)

if __name__ == '__main__':
  main()
