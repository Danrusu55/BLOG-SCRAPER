from imports import *
from functions import *

t = Twitter(
    auth=OAuth(token, token_secret, consumer_key, consumer_secret))

t.search.tweets(q="#pycon")