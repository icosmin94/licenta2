import re

import datetime
from nltk.corpus import wordnet
import nltk


class Tweet:
    def __init__(self, author="", age=0, gender="None", latitude=0,
                 longitude=0, date="", time="", raw_text="", words_count=0, words_map={}, username="", session=""):
        self.author = author
        self.age = age
        self.gender = gender
        self.latitude = latitude
        self.longitude = longitude
        if date != "" and time != "":
            date_parts = re.split('-', date)
            time_parts = re.split('[:.]+', time)
            self.date_time = datetime.datetime(year=int(date_parts[0]), month=int(date_parts[1]),
                                               day=int(date_parts[2]),
                                               hour=int(time_parts[0]), minute=int(time_parts[1]),
                                               second=int(time_parts[2]))
        self.raw_text = raw_text
        self.words_count = words_count
        self.words_map = words_map
        self.username = username
        self.session = session

    @staticmethod
    def create_tweet(entries):
        tweet = Tweet()
        tweet.__dict__.update(entries)
        return tweet


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize(tweet, contractions, stop_words, word_net_lemmatizer):
    contractionless_words = []
    processed_words = []
    words_map = {}

    words = re.split(r' ', tweet.raw_text)

    for word in words:
        if word.lower() in contractions:
            contractionless_words.extend(contractions[word.lower()])
        else:
            contractionless_words.extend([word.lower()])

    for word in contractionless_words:
        if word.endswith("'s"):
            the_word = re.sub("'s", '', word)
        else:
            the_word = word
        if the_word.__len__() > 1 and the_word not in stop_words:
            processed_words.extend([the_word])

    tagged = nltk.pos_tag(processed_words)

    for i in range(processed_words.__len__()):
        lemma = word_net_lemmatizer.lemmatize(tagged[i][0], get_wordnet_pos(tagged[i][1]))
        if lemma not in words_map:
            words_map[lemma] = 0
        words_map[lemma] = words_map[lemma] + 1

    for stop_word in stop_words:
        words_map.pop(stop_word, None)
    tweet.words_map = words_map
    tweet.words_count = sum(words_map.values())


def create_tweet(tweet_line, contractions, stop_words, word_net_lemmatizer, username, session):
    parts = re.split(r'[,"\[\]]+', tweet_line)
    author = parts[1]
    age = parts[2]
    gender = parts[3]
    latitude = parts[4]
    longitude = parts[5]
    date_time = parts[parts.__len__() - 1]
    date_time_parts = re.split('[TZ\n]+', date_time)
    raw_text = re.sub(r"[!?.\\<>\[\]()/,*:+~=\-;^\"]+", '',
                      tweet_line[tweet_line.index(parts[6]): tweet_line.index(date_time) - 1])
    raw_text = re.sub(r"[$]+", " dollar ", raw_text)

    tweet = Tweet(author, age, gender, latitude, longitude, date_time_parts[0], date_time_parts[1], raw_text, 0, {},
                  username, session)
    lemmatize(tweet, contractions, stop_words, word_net_lemmatizer)
    return tweet
