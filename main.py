import tweepy
from pushbullet import Pushbullet
import sys
import pickle
from os.path import exists
from os import mkdir

import constants

def error_check(response):
  if (len(response.errors) > 0):
    print(response.errors[0]['detail'], file=sys.stderr)
    exit(1)

if __name__ == '__main__':
  if (len(sys.argv) != 2):
    print('Expected a Twitter username to monitor', file=sys.stderr)
    exit(1)

  twt_client = tweepy.Client(
    bearer_token=constants.BEARER_TOKEN,
    consumer_key=constants.CONSUMER_KEY,
    consumer_secret=constants.CONSUMER_SECRET,
    access_token=constants.ACCESS_TOKEN, 
    access_token_secret=constants.ACCESS_TOKEN_SECRET
  )

  user_response = twt_client.get_user(username=sys.argv[1])
  error_check(user_response)

  if (not exists('./history')): mkdir('./history')

  cache_path = f'./history/{user_response.data.id}.pickle'
  history = set()

  new = not exists(cache_path)

  liked_twts = twt_client.get_liked_tweets(user_response.data.id, max_results=(100 if new else 5))
  error_check(liked_twts)
  print(f'Fetched {len(liked_twts.data)} recently liked tweets')
  
  if (new):
    history = set(map(lambda x: x.id, liked_twts.data))
    with open(cache_path, 'wb') as f:
      pickle.dump(history, f)

    print(f'New user @{user_response.data.username}\'s like history stored. Check back later.')
    exit()
  
  with open(cache_path, 'rb') as f:
    history = pickle.load(f)

  if liked_twts.data[0].id not in history:
    # new liked tweet detected
    print(f'@{user_response.data.username} liked a new tweet', f'https://twitter.com/{user_response.data.username}/likes')

    # auth PB
    try:
      pb = Pushbullet(constants.PUSHBULLET_KEY)
      pb.push_link(f'@{user_response.data.username} liked a new tweet', f'https://twitter.com/{user_response.data.username}/likes')
      print('Pushbullet notified')
    except:
      print('Failed to send PushBullet notification')

    history.add(liked_twts.data[0].id)
    with open(cache_path, 'wb') as f:
      pickle.dump(history, f)
  else:
    print('No new likes found. Have a nice day :)')
