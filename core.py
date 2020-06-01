import twitter
import json


def twitter_connection():
    with open('credentials.json') as f:
        credentials = json.load(f)

    twitter_api = twitter.Api(consumer_key=credentials['consumer_key'],
                      consumer_secret=credentials['consumer_secret'],
                      access_token_key=credentials['access_token_key'],
                      access_token_secret=credentials['access_token_secret'])

    return twitter_api

def build_test_set(twitter_api, search_keyword):
    try:
        test_tweets = twitter_api.GetSearch(search_keyword, count=10)
        print(len(test_tweets), "tweets have been fetched from twitter")
        return [{"tweet":status.text, "label":None} for status in test_tweets]

    except:
        print("Oops something went wrong. Try again later")

#main


twitter_api = twitter_connection()
test_tweets = build_test_set(twitter_api, "racism")

