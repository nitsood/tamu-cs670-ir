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

tf = defaultdict(no_use)
idf = defaultdict(float)
docs = defaultdict(list)
res = []
vocab = set()
ids = set()
doc_ctr = 0
threshold = 0.01

"""tokenize text and convert to lower case"""
def tokenize(text):
  tok = re.split(r'\W+', text, flags=re.UNICODE)
  lower_tok = []
  for t in tok:
    if(t is None or t == ''):
      continue
    lower_tok.append(t.lower())
  return lower_tok

def build_tf(doc_id, words):
  for word in words:
    tf[doc_id][word] += 1
  for word in words:
    val = tf[doc_id][word]
    tf[doc_id][word] = 1+math.log(val, 2)

def build_idf(words):
  words_uniq = set(words)
  for word in words_uniq:
    idf[word] += 1

def log_idf():
  terms = idf.keys()
  n = len(docs.keys())
  for k in terms:
    idf[k] = math.log(n/idf[k], 2)
  return

def collect(results):
  global doc_ctr
  global ids
  global vocab
  for r in results:
    #print r['Title']
    #print r['Description']
    #print
    title = tokenize(r['Title'])
    desc = tokenize(r['Description'])
    vocab = vocab.union(set(title))
    vocab = vocab.union(set(desc))
    ids.add(r['ID'])
    #tup = (title, desc)
    #tup = (r['Title'], r['Description'])
    title.extend(desc)
    docs[doc_ctr] = title
    doc_ctr += 1
  print 'collected {0} results'.format(len(results))
  print 'collected {0} ids'.format(len(ids))
  return

def calc_tfidf():
  documents = docs.keys()
  for d in documents:
    for v in vocab:
      tf[d][v] = 0
    doc_text = docs[d]
    build_tf(d, doc_text)
    #build_idf(docs[d][0])
    #build_tf(d, docs[d][1]) 
    build_idf(set(doc_text))
  log_idf()
  for d in documents:
    dimensions = tf[d].keys()
    sum_of_sq = 0.0
    for dim in dimensions:
      tf[d][dim] *= idf[dim]
      sum_of_sq += tf[d][dim]*tf[d][dim]
  #print tf  
    if sum_of_sq != 0:
      norm = math.sqrt(sum_of_sq)
      for dim in dimensions:
        tf[d][dim] /= norm
  #print tf
  return

#################### Clustering ####################

def k_means_cluster(k):
  start = set()
  clusters = defaultdict(tuple)
  for i in xrange(0, k):
    while True:
      n = get_rand(1, len(docs)-1)
      if n in start:
        continue
      start.add(n)
      s = set()
      s.add(n)
      clusters[i] = (tf[n], s) #storing the initial vector of doc n
      break
  """s = set()
  s.add(0)
  clusters[0] = (tf[0], s)
  t = set()
  t.add(2)
  clusters[1] = (tf[2], t)"""
  documents = docs.keys()
  print 'Starting at '
  print_clusters(clusters)
  print
  rss = 0.0
  ctr = 1
  for i in xrange(0, len(clusters.keys())):
    clusters[i] = (clusters[i][0], set())
  while True:
    print 'Iteration {0}'.format(ctr)
    #print
    for d in documents:
      most_similar = -1
      max_cos = -1.0
      for i in xrange(0, len(clusters.keys())):
        centroid = clusters[i][0]
        sim = get_cos_similarity(i, centroid, d)
        if sim >= max_cos:
          max_cos = sim
          most_similar = i
      clusters[most_similar][1].add(d)
      print 'Document {0} is closer to cluster {1}'.format(d, most_similar)
      #print
    new_rss = compute_rss(clusters)
    print 'old rss {0}'.format(rss)
    print 'new rss {0}'.format(new_rss)
    print
    print_clusters(clusters)
    if math.fabs(new_rss-rss) < threshold:
      print 'Change in RSS is now below the threshold of {0}. Exiting.'.format(threshold)
      break
    for i in xrange(0, len(clusters.keys())):
      new_cent = compute_centroid(clusters[i][0], clusters[i][1])
      clusters[i] = (new_cent, set())
      #clusters[i][1].clear()
    ctr += 1
    rss = new_rss
  #print_clusters(clusters)
  return

def is_stop_rss(old_rss, clusters):
  new_rss = compute_rss(clusters)
  print 'old rss {0}'.format(rss)
  print 'new rss {0}'.format(new_rss)
  #print
  if math.fabs(new_rss-rss) < threshold:
    return None
  return new_rss

def is_stop_cluster(clusters):
  return

def get_rand(begin, end):
  return random.randint(begin, end)

"""get similarity between a vector doc1 and a document id doc2;
doc1 is in vector form (term -> tf-idf value) and doc2 is just an id"""
def get_cos_similarity(cluster_num, doc1, doc2):
  cos_sum = 0.0
  terms = doc1.keys()
  for t in terms:
    cos_sum += doc1[t]*tf[doc2][t]
  print 'Cosine similarity between centroid of cluster {0} and document {1}: {2}'.format(cluster_num, doc2, cos_sum)
  return cos_sum

def print_clusters(clusters):
  print 'Total clusters: {0}'.format(len(clusters.keys()))
  for c in clusters.keys():
    print 'Cluster {0}: {1}'.format(c, clusters[c][1])
  return

def compute_centroid(prev_centroid, members):
  #prev_centroid = cluster[0]
  new_centroid = prev_centroid.copy()
  #members = cluster[1]
  for term in prev_centroid:
    s = 0.0
    k = len(members)
    for m in members:
      s += tf[m][term]
    if k != 0:
      new_centroid[term] = s/k
    else:
      new_centroid[term] = 0
  return new_centroid

def compute_rss(clusters):
  rss = 0.0
  for i in xrange(0, len(clusters.keys())):
    cent = clusters[i][0]
    members = clusters[i][1]
    terms = cent.keys()
    cluster_rss = 0.0
    for m in members:
      for t in terms:
        cluster_rss += (cent[t]-tf[m][t])*(cent[t]-tf[m][t])
    rss += cluster_rss
  return rss

#####################################################

def form_query(query):
  query = query.replace(' ', '%20')
  return '%27'+query+'%27'

def parse_json(filename):
  f = open(filename, 'r')
  lines = f.readlines()
  for line in lines:
    js = json.loads(line)
    collect(js['d']['results'])
    #collect(js)
  return

def search():
  #TODO: make this a generic function if possible
  #query_copy = query[:]
  #filename = query_copy.replace(' ', '_')+'.json'
  #f = open(filename, 'a')
  """
  f = open('texas_aggies.json', 'a')
  print 'query - texas aggies'
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27texas%20aggies%27&$format=json&$skip=0', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f) 
  f.write('\n')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27texas%20aggies%27&$format=json&$skip=15', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  f.close()
        
print 'query - texas longhorns'
  f = open('texas_longhorns.json', 'a')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27texas%20longhorns%27&$format=json&$skip=0', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27texas%20longhorns%27&$format=json&$skip=15', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  f.close()
  """
  print 'query - duke blue devils'
  f = open('duke_blue_devils.json', 'a')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27duke%20blue%20devils%27&$format=json&$skip=0', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27duke%20blue%20devils%27&$format=json&$skip=15', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  f.close()
"""
  print 'query - dallas cowboys'
  f = open('dallas_cowboys.json', 'a')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27dallas%20cowboys%27&$format=json&$skip=0', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27dallas%20cowboys%27&$format=json&$skip=15', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  #collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  f.close()
  """
  print 'query - dallas mavericks'
  f = open('dallas_mavericks.json', 'a')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27dallas%20mavericks%27&$format=json&$skip=0', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  r = requests.get('https://api.datamarket.azure.com/Bing/Search/News?Query=%27dallas%20mavericks%27&$format=json&$skip=15', auth=('niteshsood89@gmail.com', 'lDziyUrYe7njBFrdqtBb/yIxxhrH7mVHv87LidY74yM='))
  js = r.json()
  collect(js['d']['results'])
  json.dump(js, f)
  f.write('\n')
  f.close()
  return

def main():
  search()
  #parse_json('texas_aggies.json')
  #parse_json('texas_longhorns.json')
  #parse_json('duke_blue_devils.json')
  #parse_json('dallas_cowboys.json')
  #parse_json('dallas_mavericks.json')
  #parse_json('test.json')
  #print docs
  #calc_tfidf()
  #k_means_cluster(5)
  return

if __name__ == '__main__':
  main()

