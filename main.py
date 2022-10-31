import tweepy
from pushbullet import Pushbullet
import sys
import pickle
from os.path import exists

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

  cache_path = f'./history/{user_response.data.id}'
  if (not exists(cache_path)):
    with open(cache_path, mode='r') as f:
      

    print(f'New user @{user_response.data.username}\'s like history stored. Check back later.')
    exit()

  liked_twts = twt_client.get_liked_tweets(user_response.data.id)
  error_check(liked_twts)
  print(liked_twts.data)

  if (len(liked_twts.data) == 0): exit()

  for twt in liked_twts.data:
    
