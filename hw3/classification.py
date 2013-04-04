import sys
import os
import re
from collections import defaultdict
import json
import math
import requests
import pprint
import random

def no_use():
  return defaultdict(float)

""" data structures for the training set """
docs = defaultdict(list)
doc_ctr = 0
ids = set()
classes = defaultdict()
vocab = set()
p_prior = defaultdict(float)
class_tokens = defaultdict(int)
class_tf = defaultdict(no_use)

""" data structures for the test set """
test_docs = defaultdict(list)
ground = defaultdict(set) #class -> [document ids in that class]
labels = defaultdict(int)

"""tokenize text and convert to lower case"""
def tokenize(text):
  tok = re.split(r'\W+', text, flags=re.UNICODE)
  lower_tok = []
  for t in tok:
    if(t is None or t == ''):
      continue
    lower_tok.append(t.lower())
  return lower_tok

def parse_json(filename, class_name):
  f = open(filename, 'r')
  lines = f.readlines()
  num_results = 0
  for line in lines:
    js = json.loads(line)
    num_results += collect(js['d']['results'], class_name)
  prob = float(1)/num_results
  p_priori[class_name] = math.log(prob, 2)
  return

def parse_json_test_set(filename, actual_class):
  f = open(filename, 'r')
  lines = f.readlines()
  for line in lines:
    js = json.loads(line)
    collect(js['d']['results'], class_name)
  prob = float(1)/num_results
  p_priori[class_name] = math.log(prob, 2)
  return

def collect(results, class_name):
  global doc_ctr
  global ids
  global vocab
  for r in results:
    title = tokenize(r['Title'])
    desc = tokenize(r['Description'])
    vocab = vocab.union(set(title))
    vocab = vocab.union(set(desc))
    ids.add(r['ID'])
    title.extend(desc)
    docs[doc_ctr] = title
    classes[class_name].add(doc_ctr)
    class_tokens[class_name] += len(title)
    for t in title:
      class_tf[class_name][t] += 1
    doc_ctr += 1
  #print 'collected {0} results'.format(len(results))
  print 'collected {0} ids'.format(len(ids))
  return len(results)

################ Classification ################

def classify_naive_bayes():
  tdkeys = test_docs.keys()
  v = len(vocab)
  for td in tdkeys:
    terms = test_docs[td]
    max_prob = 0.0
    predicted_class = ''
    for cl in classes.keys():
      prob = p_priori[cl]
      for t in terms:
        numer = float(class_tf[cl][t]+1)
        denom = class_tokens(cl)+v
        prob += math.log(numer/denom, 2)
      if prob >= max_prob:
        max_prob = prob
        predicted_class = cl
    labels[td] = predicted_class
  return  

################################################

def search(f, query, category):
  print 'query - {0}'.format(query)
  req1 = 'https://api.datamarket.azure.com/Bing/Search/News?Query=%27{0}%27&NewsCategory=%27{1}%27&$format=json&$skip=0'.format(query, category)
  req2 = 'https://api.datamarket.azure.com/Bing/Search/News?Query=%27{0}%27&NewsCategory=%27{1}%27&$format=json&$skip=15'.format(query, category)
  r = requests.get(req1, auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f) 
  f.write('\n')
  r = requests.get(req2, auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  return

def search_ent():
  f = open('entertainment.json', 'w')
  search(f, 'bing', 'rt_Entertainment')
  search(f, 'amazon', 'rt_Entertainment')
  search(f, 'twitter', 'rt_Entertainment')
  search(f, 'yahoo', 'rt_Entertainment')
  search(f, 'google', 'rt_Entertainment')
  search(f, 'beyonce', 'rt_Entertainment')
  search(f, 'bieber', 'rt_Entertainment')
  search(f, 'television', 'rt_Entertainment')
  search(f, 'movies', 'rt_Entertainment')
  search(f, 'music', 'rt_Entertainment')
  search(f, 'obama', 'rt_Entertainment')
  search(f, 'america', 'rt_Entertainment')
  search(f, 'congress', 'rt_Entertainment')
  search(f, 'senate', 'rt_Entertainment')
  search(f, 'lawmakers', 'rt_Entertainment')
  f.close()
  return

def search_business():
  f = open('business.json', 'w')
  search(f, 'bing', 'rt_Business')
  search(f, 'amazon', 'rt_Business')
  search(f, 'twitter', 'rt_Business')
  search(f, 'yahoo', 'rt_Business')
  search(f, 'google', 'rt_Business')
  search(f, 'beyonce', 'rt_Business')
  search(f, 'bieber', 'rt_Business')
  search(f, 'television', 'rt_Business')
  search(f, 'movies', 'rt_Business')
  search(f, 'music', 'rt_Business')
  search(f, 'obama', 'rt_Business')
  search(f, 'america', 'rt_Business')
  search(f, 'congress', 'rt_Business')
  search(f, 'senate', 'rt_Business')
  search(f, 'lawmakers', 'rt_Business')
  f.close() 
  return

def search_politics():
  f = open('politics.json', 'w')
  search(f, 'bing', 'rt_Politics')
  search(f, 'amazon', 'rt_Politics')
  search(f, 'twitter', 'rt_Politics')
  search(f, 'yahoo', 'rt_Politics')
  search(f, 'google', 'rt_Politics')
  search(f, 'beyonce', 'rt_Politics')
  search(f, 'bieber', 'rt_Politics')
  search(f, 'television', 'rt_Politics')
  search(f, 'movies', 'rt_Politics')
  search(f, 'music', 'rt_Politics')
  search(f, 'obama', 'rt_Politics')
  search(f, 'america', 'rt_Politics')
  search(f, 'congress', 'rt_Politics')
  search(f, 'senate', 'rt_Politics')
  search(f, 'lawmakers', 'rt_Politics')
  f.close()
  return  

def main():
  #print 'Entertainment -----------'
  #search_ent()
  #print 'Business -----------'
  #search_business()
  #print 'Politics -----------'
  #search_politics()
  parse_json('entertainment.json', 'rt_Entertainment')
  parse_json('business.json', 'rt_Business')
  parse_json('politics.json', 'rt_Politics')
  return

if __name__ == '__main__':
  main()
