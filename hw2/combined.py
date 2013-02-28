import math
import re
import json
import heapq
from bisect import insort
from collections import defaultdict
from collections import OrderedDict

def no_use():
  """one liner used only for defaultdict's declaration.
  Could have used lambda but lambda doesn't pickle"""
  return defaultdict(float)

n_users = 0
n_tweets = 0

tf = defaultdict(no_use)
idf = defaultdict(float)
tweets = defaultdict()

"""user_names is a dictionary of user_id -> screen_name"""
user_names = OrderedDict()

"""user_names is a dictionary of user_id -> index_number"""
user_numbers = OrderedDict()

"""rev_user_numbers is a dictionary of index_number -> """
rev_user_numbers = OrderedDict()

"""heap to calculate the top 50 users"""
rank_heap = defaultdict(float)

incoming_links = defaultdict(set)
outgoing_links = defaultdict(set)

tele = 0.1
precision = 0.00000001


######################## Manager Class ######################

class RankingManager:
  def __init__(self, f, r):
    self.filename = f
    self.ranking_factor = r
    print 'Setting up data structures...'
    parse(self.filename)
    print 'Done'
    print 'Calculating tf-idf...'
    calculate_tfidf()
    print 'Done'
    print 'Ranking users...'
    rank_users()
    print 'Done'
    return
  def rank_tweets(self, query):
    q_str = defaultdict(float)
    tokens = tokenize(query)
    for token in tokens:
      q_str[token] += 1
    print 'Query: {0}'.format(q_str)
    rank_tweets_integrated(q_str, self.ranking_factor)
    return

############################################################


"""tokenize a tweet and convert to lower case"""
def tokenize(text):
  tok = re.split(r'\W+', text, flags=re.UNICODE)
  lower_tok = []
  for t in tok:
    if(t is None or t == ''):
      continue
    lower_tok.append(t.lower())
  return lower_tok

def read_file(filename):
  f = open(filename, 'r')
  lines = f.readlines()
  f.close()
  return lines


######################## PAGE RANK ############################


"""method that returns the user mentions as a dict"""
def get_users_mentioned(json_obj):
  mentions = json_obj['entities']['user_mentions']
  user_id = json_obj['user']['id']
  mentioned_users = {}
  for m in mentions:
    u = m['id']
    if(u == user_id): #self-link
      continue
    mentioned_users[u] = m['screen_name']
  #print 'The user {0} mentions {1}'.format(user_id, mentioned_users)
  return mentioned_users


def parse_json_users(json_obj):
  u = json_obj['user']
  user_id = u['id']
  screen_name = u['screen_name']
  #add_user(user_id, screen_name)
  #user_internal_id = user_names[user_id][0]
  mentioned_users = get_users_mentioned(json_obj)

  if(len(mentioned_users) > 0):
    add_user(user_id, screen_name)

  for m in mentioned_users.keys():
    add_user(m, mentioned_users[m])

    outgoing_links[user_id].add(m)
    if(user_id in incoming_links):
      pass
    else:
      incoming_links[user_id] = set()

    incoming_links[m].add(user_id)
    if(m in outgoing_links):
      pass
    else:
      outgoing_links[m] = set()
  return


"""method adds and creates a logical id for the user and adds it"""
def add_user(user_id, screen_name):
  global n_users
  #users.add(user_id) #users is a set so duplicates are taken care of
  if(user_id in user_names):
    pass
  else:
    user_names[user_id] = screen_name
    user_numbers[user_id] = n_users
    rev_user_numbers[n_users] = user_id
    n_users += 1
  return


def rank_users():
  n = n_users
  page_rank_old = [1]*n
  page_rank_new = [0]*n
  user_ids = user_names.keys()
  #print
  print n
  print len(user_ids)
  #print 'Start------'
  #print 'Old pr: '
  #print page_rank_old
  #print 'New pr: '
  #print page_rank_new
  #print
  ctr = 0
  while True:
    #print
    print 'Iteration {0}'.format(ctr)
    to_break = True
    for i in xrange(0, n):
      u = user_ids[i]
      i_links = incoming_links[u]
      if(len(i_links) == 0):
        page_rank_new[i] = tele
      else:
        x = 0.0
        for inc in i_links:
          idx = user_numbers[inc]
          y = len(outgoing_links[inc])
          x += page_rank_old[idx]/y
        x = tele + ((1-tele)*x)
        page_rank_new[i] = x
      if(math.fabs(page_rank_new[i]-page_rank_old[i]) > precision):
        to_break = False
    if(to_break == True):
      break
    #temp = page_rank_new - page_rank_old
    #print 'Old pr: '
    #print page_rank_old
    #print 'New pr: '
    #print page_rank_new
    #print 'Diff'
    #print temp
    #if(all(abs(temp) <= precision)):
    #  break
    #if(ctr == 10):
      #break
    page_rank_old[:] = page_rank_new
    ctr += 1

  #after computing page ranks, we need to find top 50
  print 'PageRank values===='
  for i in range(0, len(page_rank_new)):
    rank_heap[rev_user_numbers[i]] = page_rank_new[i]
    print '{0}: {1}'.format(user_names[rev_user_numbers[i]], page_rank_new[i])
  result = heapq.nlargest(50, rank_heap, key=rank_heap.get)
  print_users(result)
  return


########################## TF-IDF CALCULATION #######################

"""method that calculates tf dictionary"""
def parse_json_tweets(json_obj, tweet_ctr):
  s = json_obj['text']
  tweet_ctr = json_obj['id']
  #tweets[tweet_ctr] = s
  tweets[tweet_ctr] = s
  tokens = tokenize(s)
  for token in tokens:
    tf[tweet_ctr][token] += 1
  unique_tokens = set(tokens)
  #make the tokens unique to do idf calc
  for token in unique_tokens:
    idf[token] += 1
  terms = tf[tweet_ctr].keys()
  #calculate log base2 values
  for k in terms:
    tf[tweet_ctr][k] = 1+math.log(tf[tweet_ctr][k], 2)
  return


"""method that calculates tf-idf and normalizes them"""
def calculate_tfidf():
  tweet_ids = tf.keys()
  for twt_id in tweet_ids:
    terms = tf[twt_id].keys()
    sum_of_sq = 0
    for term in terms:
      tf[twt_id][term] *= idf[term]
      sum_of_sq += tf[twt_id][term]*tf[twt_id][term]
    #calculate the normalized values
    norm = math.sqrt(sum_of_sq)
    for term in terms:
      tf[twt_id][term] /= norm
  return


################### INTEGRATED TWEET RANKING ###################

"""tweet ranker"""
def rank_tweets_integrated(query_struct, ranking_factor):
  docs = tf.keys()
  top_ranked = []
  #build the tf-idf dict for the query; this is constant for all tweets
  query_terms = query_struct.keys()
  sum_of_sq = 0
  for term in query_terms:
    if(term not in idf):
      print 'No match :('
      return
    val = query_struct[term]
    val = 1+math.log(val, 2)
    val *= idf[term]
    sum_of_sq += val*val
    query_struct[term] = val
  norm = math.sqrt(sum_of_sq)
  if(norm != 0):
    for term in query_terms:
      query_struct[term] /= norm

  #now iterate through all tweets computing their score
  for doc in docs:
    #print 'Ranking tweet {0}'.format(doc)
    cosine_sum = 0.0
    terms = tf[doc]
    for t in terms:
      cosine_sum += query_struct[t]*tf[doc][t]
    tup = (doc, cosine_sum)
    #top_ranked[doc] = cosine_sum
    top_ranked.append(tup)
    #insort(top_ranked, cosine_sum)
    #s = 'Tweet {0}, score: {1}'.format(doc, cosine_sum)
    #top_ranked.append(s)
  #res = sorted(top_ranked, key=fun, reverse=True)
  print_tweets(sorted(top_ranked, key=fun, reverse=True))
  #return res[:50]
  return

def fun(tup):
  return tup[1]


########################################################

"""method that calculates tf and idf dictionaries"""
def parse(filename):
  lines = read_file(filename)
  tweet_ctr = 1
  for line in lines:
    data = json.loads(line)
    parse_json_tweets(data, tweet_ctr)
    parse_json_users(data)
    tweet_ctr += 1
  
  #once the json is parsed, we need to run over the idf dict once more
  terms = idf.keys()
  n = len(tweets.keys())
  for k in terms:
    idf[k] = math.log(n/idf[k], 2)
  return


"""build the tf-idf system for the tweets"""
"""def process_tweets(filename):
  parse(filename)
  calculate_tfidf()
  rank_users()
  #print_concise()
  return """

######################################################


def print_users(results):
  print
  print 'Results Users===='
  ctr = 1
  for r in results:
    print '{0}. {1}: {2}'.format(ctr, r, user_names[r])
    ctr += 1
  return

def print_verbose_users():
  print
  print 'No of tweets: {0}, no of users: {1}'.format(n_tweets, n_users)
  print
  print 'Users total {0} ===='.format(n_users)
  for user in user_names.keys():
    print '{0}: {1}'.format(user, user_numbers[user])
  print
  #print 'User names===='
  #print len(user_names)
  #for i in sorted(user_names.keys()):
  #  print '{0}: {1} {2}'.format(i, user_names[i])
  #print
  o_links = outgoing_links.keys()
  print 'Outgoing links total {0}===='.format(len(o_links))
  for o in sorted(o_links):
    print '{0}: {1}'.format(o, outgoing_links[o])
  print
  i_links = incoming_links.keys()
  print 'Incoming links total {0}===='.format(len(i_links))
  for i in sorted(i_links):
    print '{0}: {1}'.format(i, incoming_links[i])
  return

def print_verbose_tweets():
  print 'tweets====='
  for k in tweets.keys():
    print '{0}: {1}'.format(k, tweets[k].encode('utf-8'))
  print '\ntf======'
  for k in tf.keys():
    print '\ntweet {0}'.format(k)
    for kprime in tf[k].keys():
      print '{0}: {1}'.format(kprime.encode('utf-8'), tf[k][kprime])
  print '\nidf======'
  for k in sorted(idf.keys()):
    print '{0}: {1}'.format(k.encode('utf-8'), idf[k])
  return

def print_concise_tweets():
  print 'No of tweets: {0}'.format(len(tweets))
  print 'Size of tf dict: {0}'.format(len(tf.keys()))
  print 'Size of idf dict: {0}'.format(len(idf.keys()))

def print_tweets(top_ranked):
  #keys = top_ranked.keys()
  print '\nTweet Rankings=========='
  ctr = 0
  final = top_ranked[:50]
  for key in final:
    #print tweets[key].encode('utf-8')
    print '{0} {1}: {2}'.format(key[0], tweets[key[0]].encode('utf-8'), key[1])
  return

############################################################


"""pre-process the query and then do the ranking of tweets"""
def process_query(query):
  q_str = defaultdict(float)
  tokens = tokenize(query)
  for token in tokens:
    q_str[token] += 1
  print 'Query: {0}'.format(q_str)
  rank_tweets(q_str)
  return


def main():
  #signal.signal(signal.SIGINT, signal_handler)
  prompt = '>>'
  #n = len(sys.argv)
  #if(n != 2):
  #  print 'usage: python vector_space.py <input_json_file>'
  #  sys.exit(1)
  #dir_name = str(sys.argv[1])
  #filename  = 'b.json'
  filename = 'mars_tweets_medium.json'
  process_tweets(filename)
  #process_query('mars rover')
  while(True):
    print prompt,
    query = raw_input()
    if(query == ''):
      continue
    process_query(query)
    print
  return

if __name__ == '__main__':
  main()
