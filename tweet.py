import re
from nltk.corpus import wordnet
import nltk
from nltk.stem import WordNetLemmatizer


class Tweet:

    def __init__(self, author, age, gender, latitude,
                 longitude, date, time, raw_text, words_count, words_map):

        self.author = author
        self.age = age
        self.gender = gender
        self.latitude = latitude
        self.longitude = longitude
        self.date = date
        self.time = time
        self.raw_text = raw_text
        self.words_count = words_count
        self.words_map = words_map

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


def lemmatize(tweet, contractions, stop_words):
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
        if the_word not in stop_words and the_word.__len__() > 1:
            processed_words.extend([the_word])

    tweet.words_count = processed_words.__len__()
    tagged = nltk.pos_tag(processed_words)
    word_net_lemmatizer = WordNetLemmatizer()

    for i in range(processed_words.__len__()):
        lemma = word_net_lemmatizer.lemmatize(tagged[i][0], get_wordnet_pos(tagged[i][1]))
        if lemma not in words_map:
            words_map[lemma] = 0
        words_map[lemma] = words_map[lemma] + 1

    tweet.words_map = words_map


def create_tweet(tweet_line, contractions, stop_words):
    parts = re.split(r'[,"\[\]]+', tweet_line)
    author = parts[1]
    age = parts[2]
    gender = parts[3]
    latitude = parts[4]
    longitude = parts[5]
    date_time = parts[parts.__len__()-1]
    date_time_parts = re.split('[TZ\n]+', date_time)
    raw_text = re.sub(r"[!?.\\<>\[\]()/,*:+~=\-;^\"]+", '', tweet_line[tweet_line.index(parts[6]): tweet_line.index(date_time) - 1])

    tweet = Tweet(author, age, gender, latitude, longitude, date_time_parts[0], date_time_parts[1], raw_text, 0, {})
    lemmatize(tweet, contractions, stop_words)
    return tweet

