import configparser
from concurrent.futures import ProcessPoolExecutor
import time
import pymongo
from pymongo import MongoClient
from tweet import *
import json


def create_and_store_tweets(lines, contractions, stop_words, word_net_lemmatizer, config, task_number):
    print("Started task", task_number, ": processing:", lines.__len__(), "tweets")
    tweets = [create_tweet(tweet_line, contractions, stop_words, word_net_lemmatizer).__dict__ for tweet_line in lines]

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    tweets_collection.insert(tweets)

    print("Processed task", task_number, "with :", lines.__len__(), "tweets")


def load_tweets():

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    tweetsFile = config['default']['tweets_file']

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    tweets_collection.drop()
    # create index on date
    tweets_collection.create_index([("date", pymongo.ASCENDING)])

    batch_size = int(config['tweets']['batch_size'])
    concurrent_tasks = int(config['tweets']['concurrent_tasks'])
    executor = ProcessPoolExecutor(max_workers=concurrent_tasks)
    word_net_lemmatizer = WordNetLemmatizer()
    word_net_lemmatizer.lemmatize("dogs")

    # read stop words
    stop_words = []
    with open('./words/stop_words.txt') as sp:
        for line in sp:
            stop_words.extend([line.strip(" \n")])

    # read contractions file
    with open('./words/contractions.json') as contractions_file:
        contractions = json.load(contractions_file)

    line_number = 0
    tweets_in_batch = 0
    task_number = 0
    lines = []
    futures = []
    start = time.time()
    with open(tweetsFile) as fp:
        for line in fp:
            line_number += 1
            if line_number > 1:
                tweets_in_batch += 1
                lines += [line]
                if tweets_in_batch == batch_size:
                    submitted_lines = lines[:]

                    futures += [executor.submit(create_and_store_tweets, submitted_lines, contractions, stop_words,
                                                word_net_lemmatizer, config, task_number)]
                    tweets_in_batch = 0
                    lines = []
                    task_number += 1
                    if task_number % concurrent_tasks == 0:
                        for future in futures:
                            future.result()
                        futures = []

    if lines.__len__() > 0:
        submitted_lines = lines[:]
        futures += [executor.submit(create_and_store_tweets, submitted_lines, contractions, stop_words,
                                    word_net_lemmatizer, config, task_number)]

    for future in futures:
        future.result()
    end = time.time()

    print("Processing tweets took: ", end-start)

