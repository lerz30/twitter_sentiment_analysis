import twitter
import json
import csv
import time


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
        print(len(test_tweets), "tweets have been fetched from twitter to build the testing set")
        return [{"tweet": status.text, "label": None} for status in test_tweets]
    except Exception as e:
        print("Oops something went wrong. Try again later", e)


def fetch_tweets_by_id(tweets_ids):
    tweets_limit = 180
    fetching_window = 15*60

    train_tweets = []
    tweets_ids = tweets_ids[1350:1400]

    tweets_recovered = 0

    for tweet in tweets_ids:
        try:
            status = twitter_api.GetStatus(tweet['tweetId'])
            tweet['text'] = status.text
            train_tweets.append(tweet)
            print("tweet fetched", tweet['tweetId'])
            tweets_recovered += 1
            #time.sleep(fetching_window/tweets_limit)
        except Exception as e:
            print(tweet['tweetId'], e)
            continue

    print("We have fetched", tweets_recovered, "tweets for the trainning set")

    return train_tweets


def write_csv_output(train_tweets):
    with open('training_set.csv', 'w') as csv_output:
        csv_writer = csv.writer(csv_output, delimiter=',', quotechar="\"")
        for tweet in train_tweets:
            try:
                csv_writer.writerow([tweet["tweetId"], tweet["text"], tweet["topic"], tweet["label"]])
            except Exception as e:
                print(e)


def build_training_set():
    tweets_ids = []

    with open('corpus.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar="\"")
        for row in csv_reader:
            tweets_ids.append({'tweetId': row[2], 'label': row[1], 'topic': row[0]})

    train_tweets = fetch_tweets_by_id(tweets_ids)
    write_csv_output(train_tweets)

    return train_tweets

#main


twitter_api = twitter_connection()
test_set = build_test_set(twitter_api, "racism")
train_set = build_training_set()




