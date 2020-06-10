import re
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords
import nltk


class PreProcessTweets:
    def __init__(self):
        nltk.download('stopwords')
        nltk.download('punkt')
        self._stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

    def process_tweets(self, list_of_tweets):
        processed_tweets = []
        for tweet in list_of_tweets:
            processed_tweets.append((self._process_tweet(tweet["text"]), tweet["label"]))
        return processed_tweets

    def _process_tweet(self, tweet):
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        tweet = word_tokenize(tweet)
        return [word for word in tweet if word not in self._stopwords]