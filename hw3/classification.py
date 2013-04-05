import sys
import os
import re
import json
import math
import requests
import pprint
import random
from collections import defaultdict
from collections import OrderedDict

def no_use():
  return defaultdict(float)

""" data structures for the training set """
docs = defaultdict(list)
doc_ctr = 0
ids = set()
classes = defaultdict(set)
vocab = set()
p_prior = defaultdict(float)
class_tokens = defaultdict(int)
class_tf = defaultdict(no_use)

""" data structures for the test set """
test_ids = set()
test_docs = defaultdict(list)
ground = OrderedDict() #doc_id -> actual_class
labels = OrderedDict() #doc_id -> predicted_class

"""tokenize text and convert to lower case"""
def tokenize(text):
  tok = re.split(r'\W+', text, flags=re.UNICODE)
  lower_tok = []
  for t in tok:
    if(t is None or t == ''):
      continue
    lower_tok.append(t.lower())
  return lower_tok

######### JSON parsing and data collection ############

def parse_json_training_set(filename, class_name):
  f = open(filename, 'r')
  lines = f.readlines()
  num_results = 0
  for line in lines:
    js = json.loads(line)
    num_results += collect_training_set(js['d']['results'], class_name)
  prob = float(1)/num_results
  p_prior[class_name] = math.fabs(math.log(prob, 2))
  return

def parse_json_test_set(filename, actual_class):
  f = open(filename, 'r')
  lines = f.readlines()
  for line in lines:
    js = json.loads(line)
    collect_test_set(js['d']['results'], actual_class)
  #prob = float(1)/num_results
  #p_prior[class_name] = math.log(prob, 2)
  return

def collect_training_set(results, class_name):
  global doc_ctr
  global ids
  global vocab
  for r in results:
    title = tokenize(r['Title'])
    desc = tokenize(r['Description'])
    vocab = vocab.union(set(title))
    vocab = vocab.union(set(desc))
    i = r['ID']
    if i in ids:
      continue
    ids.add(i)
    title.extend(desc)
    docs[doc_ctr] = title
    classes[class_name].add(doc_ctr)
    class_tokens[class_name] += len(title)
    for t in title:
      class_tf[class_name][t] += 1
    doc_ctr += 1
  #print 'collected {0} results'.format(len(results))
  #print 'collected {0} ids'.format(len(ids))
  return len(results)

def collect_test_set(results, actual_class):
  global test_ids
  global doc_ctr
  for r in results:
    title = tokenize(r['Title'])
    desc = tokenize(r['Description'])
    #vocab = vocab.union(set(title))
    #vocab = vocab.union(set(desc))
    i = r['ID']
    print i
    if i in test_ids:
      print '{0} has already occured before'.format(i)
      continue
    test_ids.add(r['ID'])
    title.extend(desc)
    test_docs[doc_ctr] = title
    ground[doc_ctr] = actual_class
    #classes[class_name].add(doc_ctr)
    #class_tokens[class_name] += len(title)
    #for t in title:
      #class_tf[class_name][t] += 1
    doc_ctr += 1
  #print 'collected {0} results'.format(len(results))
  #print 'collected {0} ids'.format(len(test_ids))
  return

################ Classification ################

def classify_naive_bayes():
  tdkeys = test_docs.keys()
  v = len(vocab)
  for td in tdkeys:
    terms = test_docs[td]
    max_prob = -1.0
    predicted_class = ''
    for cl in classes.keys():
      prob = p_prior[cl]
      print 'class: {0}'.format(cl)
      for t in terms:
        numer = float(class_tf[cl][t]+1)
        denom = class_tokens[cl]+v
        prob += math.fabs(math.log(numer/denom, 2))
      print 'probability: {0}, max probability: {1}'.format(prob, max_prob)
      if prob >= max_prob:
        max_prob = prob
        predicted_class = cl
    labels[td] = predicted_class
    #break #REMOVE THIS!!!
  return  

def classification_stats():   
  print 'Actual classes--------'
  for g in ground.keys():
    print '{0}: {1}'.format(g, ground[g])
  print
  docids = test_docs.keys()
  correct = 0
  print
  for l in docids:
    print 'Document {0}: actual: {1} predicted: {2}'.format(l, ground[l], labels[l])
    if ground[l] == labels[l]:
      correct += 1
    #break
  print 'Accuracy: {0}'.format(float(correct)/len(test_docs))
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

############ RETRIEVE training set #############

def training_ent():
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

def training_business():
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

def training_politics():
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

########### RETRIEVE test set ##########

def test_entertainment():
  f = open('test_entertainment.json', 'w')
  search(f, 'apple', 'rt_Entertainment')
  search(f, 'facebook', 'rt_Entertainment')
  search(f, 'westeros', 'rt_Entertainment')
  search(f, 'gonzaga', 'rt_Entertainment')
  search(f, 'banana', 'rt_Entertainment')
  return 

def test_business():
  f = open('test_business.json', 'w')
  search(f, 'apple', 'rt_Business')
  search(f, 'facebook', 'rt_Business')
  search(f, 'westeros', 'rt_Business')
  search(f, 'gonzaga', 'rt_Business')
  search(f, 'banana', 'rt_Business')
  return

def test_politics():
  f = open('test_politics.json', 'w')
  search(f, 'apple', 'rt_Politics')
  search(f, 'facebook', 'rt_Politics')
  search(f, 'westeros', 'rt_Politics')
  search(f, 'gonzaga', 'rt_Politics')
  search(f, 'banana', 'rt_Politics')
  return

########################################

def test_classify():
  global doc_ctr
  f = 'nb_train1.json'
  g = 'nb_train2.json'
  doc_ctr = 0
  parse_json_training_set(f, 'China')
  parse_json_training_set(g, 'Not China')
  doc_ctr = 0
  f = 'nb_test.json'
  parse_json_test_set(f, 'Not China')
  classify_naive_bayes()
  classification_stats()
  return

def main():
  test_classify()
  return

  global doc_ctr
  #print 'Entertainment -----------'
  #search_ent()
  #print 'Business -----------'
  #search_business()
  #print 'Politics -----------'
  #search_politics()
  doc_ctr = 0
  parse_json_training_set('entertainment.json', 'rt_Entertainment')
  parse_json_training_set('business.json', 'rt_Business')
  parse_json_training_set('politics.json', 'rt_Politics')
  print 'Number of training ids: {0}'.format(len(ids))
  print 'Number of training docs: {0}'.format(len(docs.keys()))

  #print 'Entertainment -----------'
  #test_entertainment()
  #print 'Business -----------'
  #test_business()
  #print 'Politics -----------'
  #test_politics()
  doc_ctr = 0
  parse_json_test_set('test_entertainment.json', 'rt_Entertainment')
  parse_json_test_set('test_business.json', 'rt_Business')
  parse_json_test_set('test_politics.json', 'rt_Politics')
  print 'Number of test ids: {0}'.format(len(test_ids))
  print 'Number of test docs: {0}'.format(len(test_docs.keys()))
  
  classify_naive_bayes()
  classification_stats()
  return

if __name__ == '__main__':
  main()
