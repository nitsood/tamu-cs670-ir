import signal
import sys
from combined import RankingManager

def signal_handler(signal, frame):
  print '\nBye'
  sys.exit(0)

def no_use():
  """one liner used only for defaultdict's declaration.
  Could have used lambda but lambda doesn't pickle"""
  return defaultdict(float)

"""
class TweetRanker:
  def __init__(self, input_file, alpha):
    self.file_name = input_file
    self.alpha = alpha
"""

def main():
  filename = 'mars_tweets_medium.json'
  ranking_fact = 0.8
  r = RankingManager(filename, ranking_fact)
  r.rank_tweets('mars rover')
  return

if __name__ == '__main__':
  main()
