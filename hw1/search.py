import signal
import re
import sys
import pickle
from collections import defaultdict
from collections import OrderedDict
import inverted_index_builder
import positional_index_builder
import kgram_index_builder

def signal_handler(signal, frame):
  print '\nBye'
  sys.exit(0)

def no_use():
  """ one liner used only for defaultdict's declaration.
  Could have used lambda but lambda doesn't pickle """
  return defaultdict(list)

inverted_index = defaultdict(set)
positional_index = defaultdict(no_use)
kgram_index = defaultdict(set)
k = 2

class SearchEngine:
  def __init__(self, raw_text_dir, is_pickle):
    global positional_index
    global inverted_index
    global kgram_index
    self.dir_name = raw_text_dir
    print
    print 'Building positional index..'
    positional_index = positional_index_builder.build_positional_index(self.dir_name)
    print 'Done'
    if(is_pickle):
      positional_index_builder.write_index(positional_index)
    print 'Building inverted index..'
    inverted_index = inverted_index_builder.build_inverted_index(self.dir_name)
    print 'Done'
    if(is_pickle):
      inverted_index_builder.write_index(inverted_index)
    print 'Building kgram index..'
    kgram_index = kgram_index_builder.build_kgram_index(inverted_index)
    print 'Done'
    if(is_pickle):
      kgram_index_builder.write_index(kgram_index)
    print
    return
  def search(self, query):
    query = query.lower()
    phr = get_phrase_queries(query)
    wild = get_wildcard_queries(query)
    normal = get_normal_queries(query)
    results = []
    if(len(phr) > 0):
      results.append(self.search_positional(phr))
    if(len(wild) > 0):
      results.append(self.search_kgram(wild))
    if(len(normal) > 0):
      results.append(self.search_normal(normal))
    if(len(results) > 0):
      return set(results[0]).intersection(*results[1:])
    return results
  def search_positional(self, phrase_queries):
    return search_positional(phrase_queries)
  def search_kgram(self, kgram_queries):
    return search_kgram(kgram_queries)
  def search_normal(self, normal_queries):
    return search_normal(normal_queries, False)


############# searching normal queries #########################


def search_normal(normal_queries, is_wildcard_search):
  words = normal_queries
  postings = []
  results = set()
  for i in range(0, len(words)):
    word = words[i].lower()
    s = inverted_index[word]
    if(len(results) == 0):
      results = s
    else:
      if(is_wildcard_search):
        results = results.union(s)
      else:
        results = results.intersection(s)
  return results


############# searching phrase queries #########################


def search_positional(positional_queries):
  results = set()
  for query in positional_queries:
    postings = []
    query_words = query.split()
    for w in query_words:
      if(w not in positional_index):
        print_set(None)
        return
      else:
        docs = set(positional_index[w].keys())
        postings.append(docs)
    common_postings = set()
    if(len(postings) > 0):
      common_postings = set(postings[0]).intersection(*postings[1:])
    result = set()
    for doc in common_postings:
      occs = []
      for word in query_words:
        occs.append(positional_index[word][doc])
      modified_occs = []
      ctr = 0
      for s in occs:
        modified_occs.append([x-ctr for x in s])
        ctr += 1
      m = set()
      if(len(modified_occs) > 0):
        m = set(modified_occs[0]).intersection(*modified_occs[1:])
      if(len(m) >= 1):
        result.add(doc)
    if(len(results) == 0):
      results = result
    else:
      results = results.intersection(result)
  return results


############# searching wildcard(kgram) queries #########################


def search_kgram(kgram_queries):
  generator = kgram_index_builder.KGramGenerator('$', k)
  results = set()
  for query in kgram_queries:
    kgrams = generator.get_kgrams(query.lower()) #convert query to lowercase
    postings = set()
    for wildcard in kgrams:
      mappings = kgram_index[wildcard]
      if(len(postings) == 0):
        postings = mappings
      else:
        postings = postings.intersection(mappings)
    result = postings
    postings = post_filter(result, query)  
    doc_ids = search_normal(list(postings), True)
    if(len(results) == 0):
      results = doc_ids
    else:
      results = results.intersection(doc_ids)
  return results

def post_filter(result, wildcard_q):
  query_components = wildcard_q.split('*') #assuming that there is only one star in the query
  filtered_result = set()
  for r in result:
    if(len(query_components[0]) > 0 and len(query_components[1]) > 0 and len(r) == 1):
      continue
    if(r.startswith(query_components[0]) and r.endswith(query_components[1])):
      filtered_result.add(r)
  return filtered_result


################################################################


def get_phrase_queries(query):
  phr = []
  for p in re.findall(r'\".*?\"', query): 
    if(p.startswith('\"') and p.endswith('\"')):
      phr.append(p[1:-1])
  return phr

def get_wildcard_queries(query):
  non_phrase = re.split(r'\".*?\"', query)
  wild = []
  for w in non_phrase:
    words = w.split()
    for a in words:
      if(a.find('*') != -1):
        wild.append(a.strip())
  return wild

def get_normal_queries(query):
  non_phrase = re.split(r'\".*?\"', query)
  normal = []
  for w in non_phrase:
    words = w.split()
    for a in words:
      if(a.find('*') == -1):
        normal.append(a.strip())
  return normal

def print_set(s):
  if(s is not None and len(s) != 0):
    for p in s:
      print '{0} '.format(p),
    print
  else:
    print 'No match'
  return


########################### main() ###############################


def main():
  signal.signal(signal.SIGINT, signal_handler)
  prompt = '>>'
  n = len(sys.argv)
  if(n < 2 or n > 3):
    print 'usage: python search.py <doc_directory> [--pickle]'
    sys.exit(1)
  dir_name = str(sys.argv[1])
  if(not dir_name.endswith('/')):
    dir_name += '/'
  is_pickle = False
  if(n == 3):
    is_pickle = True
  ##instantiate the SearchEngine class
  se = SearchEngine(dir_name, is_pickle)
  while(True):
    print prompt,
    query = raw_input()
    if(query == ''):
      continue
    res = se.search(query)
    print 
    print_set(sorted(res))
    print
  return 

if __name__ == '__main__':
  main()
