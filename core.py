import twitter
import json
import csv
import time
import pre_processor as pp
import nltk


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
        return [{"text": status.text, "label": None} for status in test_tweets]
    except Exception as e:
        print("Oops something went wrong. Try again later", e)


def fetch_tweets_by_id(tweets_ids):
    tweets_limit = 180
    fetching_window = 15*60
    train_tweets = []

    for tweet in tweets_ids:
        try:
            status = twitter_api.GetStatus(tweet['tweetId'])
            tweet['text'] = status.text
            train_tweets.append(tweet)
            print("tweet fetched", tweet['tweetId'])
            time.sleep(fetching_window/tweets_limit)
        except Exception as e:
            print(tweet['tweetId'], e)
            continue

    print("We have fetched", len(train_tweets), "tweets for the trainning set")
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


def get_training_set():
    tweets_list = []
    with open('training_set.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar="\"")
        for row in csv_reader:
            tweets_list.append({'tweetId': row[0], 'label': row[3], 'topic': row[2], 'text': row[1]})
    if len(tweets_list) == 0:
        return build_training_set()
    return tweets_list


def build_vocabulary(pre_processed_train_set):
    all_words = []

    for (words, sentiment) in pre_processed_train_set:
        all_words.extend(words)

    wordlist = nltk.FreqDist(all_words)
    word_features = wordlist.keys()

    return word_features


def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in tweet_words)
    return features


#main
pre_process = pp.PreProcessTweets()

twitter_api = twitter_connection()
test_set = build_test_set(twitter_api, "racism")
train_set = get_training_set()

pre_processed_test_set = pre_process.process_tweets(test_set)
pre_processed_train_set = pre_process.process_tweets(train_set)
word_features = build_vocabulary(pre_processed_train_set)
training_features = nltk.classify.apply_features(extract_features, pre_processed_train_set)
NBayesClassifier = nltk.NaiveBayesClassifier.train(training_features)
NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in pre_processed_test_set]

if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
    print("Overall Positive Sentiment")
    print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
else:
    print("Overall Negative Sentiment")
    print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")





